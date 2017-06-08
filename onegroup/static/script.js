function displayForm() {
   document.getElementById('formDivleft').style.display = "block";
}

function submitForm() {
    var email1 = document.forms["userForm"]["email1"].value;
    var pass1 = document.forms["userForm"]["pass1"].value;
    var atpos = email1.indexOf("@");
    var dotpos = email1.lastIndexOf(".");
    if (atpos<1 || dotpos<atpos+2 || dotpos+2>=email1.length) {
        alert("Not a valid e-mail address");
        return false;
    }
    alert("Not a valid e-mail address");
    return true;
}