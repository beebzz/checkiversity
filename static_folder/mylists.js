/* -------------------------------------------------------------------------------------
THIS IS FOR THE LIST OF TITLES (NOT TO BE CONFUSED WITH THE LIST OF ITEMS)
------------------------------------------------------------------------------------- */

/* -------------------------------------------------------------------------------------
For Style, came with template
------------------------------------------------------------------------------------- */

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

// To press enter to submit the new list item
$("#myInput").keypress(function(event) {
    if (event.which == 13) {
        event.preventDefault();
        $("#new_list").click();
    }
});

/* -------------------------------------------------------------------------------------
 To delete an item from the list
------------------------------------------------------------------------------------- */

// Listens for the user to click the x button
function addDeleteListener() {
  var close = document.getElementsByClassName("close");
  var i;
  for (i = 0; i < close.length; i++) {
    close[i].onclick = function() {
      var div = this.parentElement;
      deleteElement(div);
    }
  }
}

// Deletes the element, runs a function back to python, sets display to none
function deleteElement(listElement) {
  var text = $(listElement).text();
  var listTitle = text.slice(0,-1) // Removes the x from the element's text
  $.post('/deleteList', {"listTitle": listTitle})
  listElement.style.display = "none";
}

/* -------------------------------------------------------------------------------------
 To create a new item based on the input
------------------------------------------------------------------------------------- */

// Create a new list item when clicking on the "Add" button
function newCheckList() {
  var name = $("#myInput").val(); // Takes the input from the user
  doPost("/saveList", {"name":name}, newCheckListCreated)
}

// Takes the data and sends it to Python as a JSON stringified
function doPost(url, data, success) {
  $.ajax({
    type: "POST",
    url: url,
    data: JSON.stringify(data), // This is the input value
    contentType:"application/json; charset=utf-8",
    dataType:"json", // Should this be a string
    success: success, // Referencing the function, newItemCreated, to run through after it finishes ajax
  });
}

var newCheckListCreated = function (data, textStatus) {
  $("#results").text("")
  // To create a list element with a link isnide it
  var li = document.createElement("li");
  var a = document.createElement("a");
  var inputValue = document.getElementById("myInput").value;
  var linkText = document.createTextNode(inputValue);
  // For the url, to acess the specific key/id
  var base_url = "/checklist?id=";
  var url_safe_id = data;
  var link = base_url + url_safe_id;
  // Appends values together
  a.appendChild(linkText);
  li.appendChild(a);
  a.title = inputValue;
  a.href = link;
  if (inputValue === '') {
    // Alerts the user if they wrote nothing
    alert("You must write something!");
  } else {
    // Appends the item to the page, as long as it is not an empty string
    document.getElementById("myUL").appendChild(li);
  }

  // Adds the x's
  document.getElementById("myInput").value = "";
  var span = document.createElement("SPAN");
  var txt = document.createTextNode("\u00D7");
  span.className = "close";
  span.appendChild(txt);
  li.appendChild(span);

  // Deletes a new element if clicked
  for (i = 0; i < close.length; i++) {
    close[i].onclick = function() {
      var listElement = this.parentElement;
      deleteElement(listElement);
    }
  }
};

/* -------------------------------------------------------------------------------------
 To take the titles from Data Store and show them on the screen when the page refreshes
------------------------------------------------------------------------------------- */

// When page loads will call the function returnList
$(document).ready(function(){
  returnTitles()
});

// When the page is refreshed it runs
function returnTitles() {
  doGet("/returnTitles", refreshTitles);
}

// Gets the data from the python
function doGet(url, success) {
  $.ajax({
    type: "GET",
    url: url,
    contentType:"application/json; charset=utf-8",
    dataType:"json",
    success: success,
  });
}

// Takes the Lists from Data Store and populates the UI with list items that include the contents and an x
var refreshTitles = function (data) {
  var objects = data;
  for (var i = 0; i < objects.length; i ++) {
    // Creates the list element (with a link) which is added to the page
    var t = document.createTextNode(objects[i]['name']);
    var li = document.createElement("li");
    var a = document.createElement("a");
    // For the url, to acess the specific key/id
    var base_url = "/checklist?id=";
    var url_safe_id = objects[i]['key'];
    var link = base_url + url_safe_id;
    if (t.wholeText == '') {
      // If it is an empty string, it never places it in the body
    }
    else {
      // To place into the body
      a.appendChild(t);
      li.appendChild(a);
      a.href = link;
      document.getElementById("myUL").appendChild(li);
      // To add the x:
      var span = document.createElement("SPAN");
      var txt = document.createTextNode("\u00D7");
      span.className = "close";
      span.appendChild(txt);
      li.appendChild(span);
    };
    addDeleteListener(); // Allows you to delete item, waits for click
  }
};
