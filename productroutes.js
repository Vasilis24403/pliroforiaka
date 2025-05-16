// delete todo
consttodoListUl=document.querySelector("#todo-list ul");
todoListUl.addEventListener('click', function(event){
    if (event.target.className=='mark-done') {
        constclickedButton=event.target;
        consttodoToRemove=clickedButton.parentElement;
        console.log(`Congratulations on finishing the todo '${todoToRemove.children[0].textContent}'`)
        todoToRemove.parentElement.removeChild(todoToRemove);
    }
});

// add todo
constaddForm=document.forms['add-todo'];
addForm.addEventListener('submit', function(event){
    event.preventDefault();
    constinputField=addForm.querySelector('input[type="text"]');
    consttodoValue=inputField.value;
    if(todoValue.length==0) {
        return;
    }
    
    inputField.value=""  // clear the input field

    // create elements
    constliToInsert=document.createElement("li");
    constspanTodoValueToInsert=document.createElement("span");
    spanTodoValueToInsert.textContent=todoValue;
    spanTodoValueToInsert.classList.add("name");

    constspanButtonToInsert=document.createElement("span");
    spanButtonToInsert.textContent="Mark Done";
    spanButtonToInsert.classList.add('mark-done');

    // append span tags to li
    liToInsert.appendChild(spanTodoValueToInsert);
    liToInsert.appendChild(spanButtonToInsert);
    todoListUl.appendChild(liToInsert);
});

// hide todos
consthideTodosCheckbox=document.querySelector('input[type="checkbox"]');
hideTodosCheckbox.addEventListener('change', function(event){
    constliTodos=document.querySelectorAll("#todo-list li");
    liTodos.forEach(function(li){
        constcurrentDisplay=li.style.display;
        li.style.display= (hideTodosCheckbox.checked) ?'none':'inherit';
    });
});

//search todos
constsearchBar=document.forms['search-todos'].querySelector('input[type="text"]');
console.log(searchBar);
searchBar.addEventListener('keyup', function(event){
    console.log("Some key was pressed!");
    Array.from(todoListUl.children).forEach(function(li){
        constsearchQuery=searchBar.value.toLowerCase();
        consttodoDescription=li.firstElementChild.textContent.toLowerCase();
        console.log(`Searching for ${searchQuery} inside ${todoDescription}`)
        li.style.display= (todoDescription.includes(searchQuery)) ?'inherit':'none';
    });
});


