function confirmBorrow(DestURL){
	var borrow = confirm("Are you sure you want to borrow this tool?");
	if (borrow) {location.href = DestURL;}
	return borrow;
}

function confirmReturn(DestURL){
	var returnTool = confirm("Are you sure you want to return this tool?");
	if (returnTool) {location.href = DestURL;}
	return returnTool;
}

function showTools(){
	/**
	* Renders the tools table, hiding the users table.
	* @author Grant Gadomski
	*/
	document.getElementById('tools').style.display = 'block';
	document.getElementById('users').style.display = 'none';
	splitIntoPages();
}

function showUsers(){
	/**
	* Renders the users table, hiding the tools table.
	* @author Grant Gadomski
	*/
	document.getElementById('users').style.display = 'block';
	document.getElementById('tools').style.display = 'none';
	splitIntoPages();
}

function toolCondition(){
	/**
	* Hides all tools in the tool table that are not of the condition currently selected.
	* @author Grant Gadomski
	*/
	var conditionElement = document.getElementById('tool_condition_selection');
	var condition = parseInt(conditionElement.options[conditionElement.selectedIndex].value);
	var searchBar = document.getElementById('tool_search').value;
	var toolTable = document.getElementById('tool_table');
		
	for (var i = 1, row; row = tool_table.rows[i]; i++){
		row.style.display = '';
		if (condition != 1000){
			if (parseInt(row.cells[3].id) > condition){
				row.style.display = 'none';
			}
			else {
				toolType(row);
			}
		}
		else {
			toolType(row);
		}
	}
}

function toolType(row){
	/**
	* Hides all tools not of the given type.
	* @author Grant Gadomski
	*/
	var typeElement = document.getElementById('tool_type_selection');
	var type = typeElement.options[typeElement.selectedIndex].text;
	var searchBar = document.getElementById('tool_search').value;
	var toolTable = document.getElementById('tool_table');

	if (type != "All Types"){
		if (row.cells[2].innerText != type){
			row.style.display = 'none';
		}
		else {
			toolSearch(row);
		}
	}
	else {
		toolSearch(row);
	}
}

function toolSearch(row){
	/**
	* Displays all tools with the given letters in their names.
	* Parses through the name of each tool, seeing if it contains
	* the sequesnce of letters being searched.
	* @author Grant Gadomski
	*/
	var rawSearchString = document.getElementById('tool_search').value.toLowerCase();
	var searchStrings = rawSearchString.split(" ");
	for (var h = 1; h < searchStrings.length; h++){
		if (searchStrings[h] == ''){
			searchStrings.splice(h, 1);
			h--;
		}
	}

	var toolTable = document.getElementById('tool_table');
	
	var deleteRow = true;
	for (var j = 0; j < searchStrings.length; j++){
		searchString = searchStrings[j];
		toolName = row.cells[0].innerText.toLowerCase();
		owner = row.cells[1].innerText;

		if (toolName.indexOf(searchString) == -1){
			if (owner.indexOf(searchString) == -1){
				deleteRow = true;
			}
			else {
				deleteRow = false;
				break;
			}
		}
		else {
			deleteRow = false;
			break;
		}
	}

	if (deleteRow == true) {
		row.style.display = 'none';
	}
	splitIntoPages();
}

function userSearch(){
	/**
	* Displays all users with the given letters in their names.
	* @author Grant Gadomski
	*/
	var rawSearchString = document.getElementById('user_search').value.toLowerCase();
	var searchStrings = rawSearchString.split(" ");
	for (var h = 1; h < searchStrings.length; h++){
		if (searchStrings[h] == ''){
			searchStrings.splice(h, 1);
			h--;
		}
	}

	var userTable = document.getElementById('user_table');

	for (var i = 1, row; row = userTable.rows[i]; i++){
		for (var j = 0; j < searchStrings.length; j++){
			searchString = searchStrings[j];
			userName = row.cells[0].innerText.toLowerCase();
			userEmail = row.cells[1].innerText.toLowerCase();

			if (userName.indexOf(searchString) == -1){
				if (userEmail.indexOf(searchString) == -1){
					row.style.display = 'none';
				}
				else {
					row.style.display = '';
					break;
				}
			}
			else {
				row.style.display = '';
				break;
			}
		}
	}
	splitIntoPages();
}

function splitIntoPages(){
	/**
	* Gets the dropdown specifying how many tools to display on a
	* page, and the indicator of what page the user's currently on.
	*@author Grant Gadomski
	*/
	numberPerPageElement = document.getElementById('number_per_page');
	numberPerPage = parseInt(numberPerPageElement.options[numberPerPageElement.selectedIndex].value);
	pageNumber = parseInt(document.getElementById('current_page').innerHTML);

	currentTopLimit = (pageNumber * numberPerPage) + 1;
	currentBottomLimit = (currentTopLimit - numberPerPage);

	table = document.getElementById('tool_table');
	if (document.getElementById('users').style.display != 'none'){
		table = document.getElementById('user_table');
	}

	var i = currentBottomLimit; //Counting amount of visible elements.
	var j = currentBottomLimit; //Actual counter

	while (i < currentTopLimit && j < table.rows.length) {
		row = table.rows[j];

		if (row.style.display != 'none') {
			i++;
		}
		j++;
	}

	while (j < table.rows.length) {
		table.rows[j].style.display = 'none';
		j++;
	}

	var h = 1;
	while (h < currentBottomLimit) {
		table.rows[h].style.display = 'none';
		h++;
	}
}

function changeNumberOnPage(){
	/**
	* Changes the amount of tools being displayed on page.
	* @author Grant Gadomski
	*/
	for (var i = 1, row; row = tool_table.rows[i]; i++){
		row.style.display = '';
	}

	if (document.getElementById('users').style.display != 'none') {
		userSearch();
		splitIntoPages();
	}
	else {
		toolCondition();
		splitIntoPages();
	}
}

function goPageBack(){
	/**
	* Goes back to the previous page.
	* @author Grant Gadomski
	*/
	currentPageElement = document.getElementById('current_page');
	currentPageNumber = parseInt(currentPageElement.innerHTML);

	if (currentPageNumber > 1) {
		currentPageNumber -= 1;
		currentPageElement.innerHTML = currentPageNumber;
		changeNumberOnPage();
	}
}

function goPageForward(){
	/**
	* Goes forward to the next page.
	* @author Grant Gadomski
	*/
	currentPageElement = document.getElementById('current_page');
	currentPageNumber = parseInt(currentPageElement.innerHTML);
	numberPerPageElement = document.getElementById('number_per_page');
	numberPerPage = parseInt(numberPerPageElement.options[numberPerPageElement.selectedIndex].value);
	table = document.getElementById('tool_table');
	if (document.getElementById('users').style.display != 'none'){
		table = document.getElementById('user_table');
	}
	rows = table.rows.length;
	pageDecision = rows/((numberPerPage * currentPageNumber) + 1);

	if (pageDecision > 1){
		currentPageNumber += 1;
		currentPageElement.innerHTML = currentPageNumber;
		changeNumberOnPage();
	}
}

function backToFirstPage(){
	/**
	* Allows user to navigate back to first page of elements.
	* @author Grant Gadomski
	*/
	document.getElementById('current_page').innerHTML = 1;
	changeNumberOnPage();
}