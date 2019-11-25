function createAlert(message, category) {
  var box = document.createElement("div");
  box.innerText = message;
  box.classList.add("alert");
  box.classList.add(category);
  var bnt = document.createElement("span");
  bnt.classList.add("closebtn");
  bnt.onclick = function () { this.parentElement.style.display = 'none'; };
  bnt.innerText = "×";
  var mess = document.createElement("strong");
  mess.innerText = category;
  box.appendChild(bnt);
  box.appendChild(mess);
  document.body.insertBefore(box, document.body.childNodes[0]);
}

function togg_element_onclick(checkbox_id, ...elements) {
  const checkbox = document.getElementById(checkbox_id);
  if (checkbox.checked == false) {
    for (let i = 0; i < elements.length; i++) {
      const selected_element = document.getElementById(elements[i]);
      selected_element.disabled = false;
    }
  } else {
    for (let i = 0; i < elements.length; i++) {
      const selected_element = document.getElementById(elements[i]);
      selected_element.disabled = true;
    }
  }
}
function password_char_check(password) {
  // at least one number, one lowercase and one uppercase letter
  // at least 8 characters
  var re = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}/;
  return re.test(password);
}

function validate_password(pass_1_id, pass_2_id, username_id) {
  pass_1_id = document.getElementById(pass_1_id).value;
  pass_2_id = document.getElementById(pass_2_id).value;
  username_id = document.getElementById(username_id).value;
  if (pass_1_id != pass_2_id) {
    createAlert("Passwords do not match!", "warning");
    return false;
  } else if (pass_1_id == username_id) {
    createAlert("Password cannot be username", "warning");
    return false;
  } else if (password_char_check(pass_1_id) == false) {
    createAlert(
      "Password must have more than 8 characters, upper and lowercase, a number and symbol!",
      "warning"
    );
    return false;
  }
  return true;
}

function new_task() {
  var task_content = window.prompt("Whats the task content?");
  if (task_content != null) {
    var task_elem = document.createElement("input");
    task_elem.setAttribute("type", "text");
    task_elem.setAttribute("name", "atask");
    task_elem.setAttribute("value", task_content);
    document.getElementById("created_tasks").append(task_elem);
  }
}

function remove_elem_children(elem){
  // removes a given elements children
  while (elem.hasChildNodes()){
    elem.removeChild(elem.lastChild);
  }
}

function httpGetAsync(theUrl, callback) {
  // source: https://stackoverflow.com/questions/247483/http-get-request-in-javascript
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function () {
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
      callback(xmlHttp.responseText);
  }
  xmlHttp.open("GET", theUrl, true); // true for asynchronous 
  xmlHttp.send(null);
}

function load_options_to_select(raw_options) {
  var parsed = JSON.parse(raw_options);
  for (i in parsed.sublocs){
    console.log(parsed[i].name);
  }
}

function start_load_options_to_select(select_id, url, main_loc_id){
  // TODO: enable/disable when async has started and finished
  var select_elem = document.getElementById(select_id);
  var main_loc = document.getElementById(main_loc_id);
  remove_elem_children(select_elem);
  url = url + "?mainloc=" + main_loc.options[main_loc.selectedIndex].text;
  httpGetAsync(url, load_options_to_select)
}
