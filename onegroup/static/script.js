function displayForm() {
   document.getElementById('formDivleft').style.display = "block";
}

function checkForm() {
  // Currently not working
    document.getElementById('submitDiv').style.display = "block";
    var email1 = document.forms["userForm"]["email1"].value;
    var pass1 = document.forms["userForm"]["pass1"].value;
    var atpos = email1.indexOf("@");
    var dotpos = email1.lastIndexOf(".");
    if (atpos<1 || dotpos<atpos+2 || dotpos+2 >= email1.length) {
        alert("Not a valid e-mail address");
        document.getElementById('submitDiv').style.display = "block";
        return false;
    }
    else {
      document.getElementById('submitDiv').style.display = "block";
      return true;
    }
}
