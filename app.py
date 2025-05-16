from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:5500"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# MongoDB Configuration
def get_mongo_client():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        logger.error("❌ MONGO_URI not found in environment variables")
        raise ValueError("MongoDB connection string not configured")

    try:
        client = MongoClient(
            mongo_uri,
            connectTimeoutMS=5000,
            socketTimeoutMS=30000,
            serverSelectionTimeoutMS=5000,
            retryWrites=True,
            retryReads=True
        )
        # Test the connection
        client.admin.command('ping')
        logger.info("✅ Successfully connected to MongoDB!")
        return client
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {str(e)}")
        raise

# Initialize MongoDB connection
try:
    mongo_client = get_mongo_client()
    db = mongo_client["bagalicious"]
    products_collection = db["products"]
except Exception as e:
    logger.error(f"❌ Failed to initialize MongoDB: {str(e)}")
    # Exit if we can't connect to MongoDB
    exit(1)

# Helper Functions
def serialize_product(product):
    """Convert MongoDB document to JSON-serializable format"""
    if product is None:
        return None
    product['_id'] = str(product['_id'])
    return product

# Database Initialization
def initialize_database():
    """Ensure database contains sample products"""
    sample_products = [
        {
            "title": "Adidas Duffel Bag",
            "description": "Blue sports duffel bag with shoulder strap",
            "image": "sport4a.jpeg",
            "category": "sports",
            "likes": 0,
            "created_at": datetime.utcnow()
        },
        {
            "title": "Nike Backpack",
            "description": "Black everyday backpack with laptop compartment",
            "image": "backpack1.jpeg",
            "category": "backpacks",
            "likes": 0,
            "created_at": datetime.utcnow()
        }
    ]

    try:
        if products_collection.count_documents({}) == 0:
            result = products_collection.insert_many(sample_products)
            logger.info(f"📦 Inserted {len(result.inserted_ids)} sample products")
        else:
            count = products_collection.count_documents({})
            logger.info(f"📊 Found {count} existing products")
    except Exception as e:
        logger.error(f"⚠️ Database initialization error: {str(e)}")

# API Endpoints
@app.route('/popular-products', methods=['GET'])
def get_popular_products():
    """Get top 20 most liked products"""
    try:
        products = list(products_collection.find()
                       .sort("likes", -1)
                       .limit(20))
        return jsonify([serialize_product(p) for p in products])
    except Exception as e:
        logger.error(f"Error in /popular-products: {str(e)}")
        return jsonify({"error": "Failed to fetch products"}), 500

@app.route('/products-by-category', methods=['GET'])
def get_products_by_category():
    """Get products filtered by category"""
    try:
        category = request.args.get('category')
        if not category:
            return jsonify({"error": "Category parameter is required"}), 400
            
        products = list(products_collection.find({"category": category}))
        return jsonify([serialize_product(p) for p in products])
    except Exception as e:
        logger.error(f"Error in /products-by-category: {str(e)}")
        return jsonify({"error": "Failed to fetch products by category"}), 500

@app.route('/search', methods=['GET'])
def search_products():
    """Search products by title or description"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify([])
            
        products = list(products_collection.find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        }))
        return jsonify([serialize_product(p) for p in products])
    except Exception as e:
        logger.error(f"Error in /search: {str(e)}")
        return jsonify({"error": "Search failed"}), 500

@app.route('/like', methods=['POST'])
def like_product():
    """Increment product like count"""
    try:
        data = request.get_json()
        product_id = data.get('id')
        
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400
            
        result = products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"likes": 1}}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Product not found"}), 404
            
        return jsonify({"success": True, "message": "Like added"})
    except Exception as e:
        logger.error(f"Error in /like: {str(e)}")
        return jsonify({"error": "Failed to update like count"}), 500

@app.route('/healthcheck', methods=['GET'])
def health_check():
    """Server health check endpoint"""
    try:
        # Test both Flask and MongoDB
        mongo_client.admin.command('ping')
        return jsonify({
            "status": "healthy",
            "server_time": datetime.utcnow().isoformat(),
            "database": "connected",
            "products_count": products_collection.count_documents({})
        })
    except Exception as e:
        logger.error(f"Healthcheck failed: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# Initialize the database
initialize_database()

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start Flask server: {str(e)}")