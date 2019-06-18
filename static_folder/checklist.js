/* -------------------------------------------------------------------------------------
THIS IS FOR THE LIST OF ITEMS (NOT TO BE CONFUSED WITH THE LIST OF TITLES)
------------------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------------------
For Style, came with template
------------------------------------------------------------------------------------- */
//

// Create a "close" button and append it to each list item
var myNodelist = document.getElementsByTagName("LI");
var i;
for (i = 0; i < myNodelist.length; i++) {
  var span = document.createElement("SPAN");
  var txt = document.createTextNode("\u00D7");
  span.className = "close";
  span.appendChild(txt);
  myNodelist[i].appendChild(span);
}

// Add a "checked" symbol when clicking on a list item
var list = document.querySelector('ul');
list.addEventListener('click', function(ev) {
  if (ev.target.tagName === 'LI') {
    ev.target.classList.toggle('checked');
    // Also want to change completion status ?
  }
}, false);

// Creates item when you press enter button instead of clicking the add button
$("#myInput").keypress(function(event) {
    if (event.which == 13) {
        event.preventDefault();
        $("#new_item").click();
    }
});
/* -------------------------------------------------------------------------------------
 To delete an item from the list
------------------------------------------------------------------------------------- */

// This will be called when you close the item (press the x)
function deleteElement(listElement) {
  var text = $(listElement).text();
  var itemText = text.slice(0,-1) // Removes the x from the list's text
  $.post('/deleteItem', {"itemText": itemText})
  listElement.style.display = "none";
}

// Listens for when the button is clicked to close the item
function addDeleteListener() {
  if (GlobalEditable == 'False') {
    console.log ("This is not the owner-- do nothing")
  }
  else {
    var close = document.getElementsByClassName("close");
    var i;
    for (i = 0; i < close.length; i++) {
      close[i].onclick = function() {
        var div = this.parentElement;
        deleteElement(div);
  }
    }
  }
}

/* -------------------------------------------------------------------------------------
 To create a new item based on the input
------------------------------------------------------------------------------------- */

// Create a new list item when clicking on the "Add" button (Called by the add button in the HTML)
function newElement() {
  var name = $("#myInput").val();
  var id = $("#key").val();
  doPost("/saveItem", {"name":name, "id": id}, newItemCreated) // /saveitem calls the handler, then executes the handler
}

// Takes the data and sends to Python
function doPost(url, data, success) {
  $.ajax({
    type: "POST",
    url: url,
    data: JSON.stringify(data),
    contentType:"application/json; charset=utf-8",
    dataType:"json",
    success: success, // Referencing the function, newItemCreated, to run through after it finishes ajax
  });
}

// Each time an element is created
var newItemCreated = function (data, textStatus) {
  // Creates list items
  $("#results").text("")
  var li = document.createElement("li");
  var inputValue = document.getElementById("myInput").value;
  var t = document.createTextNode(inputValue);
  li.appendChild(t);
  // Checks to see if it is an empty string or not
  if (inputValue === '') {
    alert("You must write something!");
  } else {
    document.getElementById("myUL").appendChild(li);
  }
  document.getElementById("myInput").value = "";
  // To add the x's
  var span = document.createElement("SPAN");
  var txt = document.createTextNode("\u00D7");
  span.className = "close";
  span.appendChild(txt);
  li.appendChild(span);
  // Listens for when the x's are clicked
  addDeleteListener();
    };

/* -------------------------------------------------------------------------------------
 To take the items from Data Store and show them on the screen when the page refreshes
------------------------------------------------------------------------------------- */

// When page loads will call the function returnList
$(document).ready(function(){
  returnList();
});

// When the page is refreshed it runs
function returnList() {
  var id = $("#key").val();
  $.get( "/returnList", { "id": id}, refreshItems, 'json'); // Passes ID
}

// Gets the data
function doGet(url, success) {
  $.ajax({
    type: "GET",
    url: url,
    contentType:"application/json; charset=utf-8",
    success: success,
  });
}

// Takes the objects from Data Store and populates the UI with list items that include the contents and an x
var refreshItems = function (data) {
  var objects = data;
  for (var i = 0; i < objects.length; i ++) {
    // To add the list items
    var t = document.createTextNode(objects[i]['name']);
    var li = document.createElement("li");
    // Checks to see if the string is empty
    if (t.wholeText == '') {
    }
    else {
    li.appendChild(t);
    document.getElementById("myUL").appendChild(li);
    // To add the x:
    var span = document.createElement("SPAN");
    var txt = document.createTextNode("\u00D7");
    span.className = "close";
    span.appendChild(txt);
    li.appendChild(span);
  };
  };
  // Listens for the user to click the x button
  addDeleteListener();
};

/* -------------------------------------------------------------------------------------
STRETCH-- allows you to copy lists and change titles on copied lists
------------------------------------------------------------------------------------- */
returnListKey();

addTitleChangeListener();

function addTitleChangeListener() {
  var id = $("#key").val();
  $.get( "/checkCopyableAttribute", { "id": id}, addTitleChangeButton, 'text');
  // Looks to see if it is a copy or not
}

function addTitleChangeButton(copied){
  console.log (copied);
  if (copied == 'True') {
    var $input = $('<div id= "center_button"><input id = "changetitle" type="button" onclick="changeTitle();" value="Change Title" class="button"/></div');
    $input.appendTo($("body"));
    console.log ('can change title')
  }
  else {
    console.log ('dont show button')
  };
}

function changeTitle(){
  var new_title = prompt("Please enter your new title");
  var id = $("#key").val();
  if (new_title != null) {
    doPost( "/changeTitle", {"new_title": new_title, "id": id}, null);
}
  console.log('change the title');
  window.location.reload(true);
}

function returnListKey() {
  var id = $("#key").val();
  $.get( "/verifyEditor", { "id": id}, insertCopyButton, 'text'); // Decide what you want to do with returned JSON?
}

var GlobalEditable = 'True'; // True = editable, False = not editable

// Need to make it so only if the user is verified
function insertCopyButton(editable) {
  console.log (editable);
  if (editable == 'False') {
    var $input = $('<div id ="try" ><input id = "copy" type="button" onclick="makeCopyOfList();" value="Copy List" class="button"/></div>');
    $input.appendTo($("body"));
    console.log ('no edits')
    GlobalEditable = 'False';
    addEditableListener() // Listens for the global variable to change
  }
  else {
    console.log ('allow edits')
  };
  window.editable = GlobalEditable;
};

// listener to disable button for buttons on page remove listeners

function addEditableListener() {
  console.log ('Running')
  console.log (GlobalEditable)
  if (GlobalEditable == 'False') {
    var localEditable = (GlobalEditable != 'False');
    console.log (localEditable);
    // Disable click listeners
    document.getElementById("new_item").onclick = null;
  }
  else {
    console.log ('do nothing allow edits')
  }
}

function makeCopyOfList() {
  console.log ('hello')
  var id = $("#key").val();
  $.get( "/copyList", { "id": id}, presentNewList, 'text');
  // Some how get key
  // Here I want to redirect and bring them to a new list
}

function presentNewList(urlsafe) {
  console.log ("maybe pop")
  var base_url = "/checklist?id=";
  var url_safe_id = urlsafe;
  var link = base_url + url_safe_id;
  console.log('new url')
  $(location).attr('href', link)
}
