// $(document).ready(function () {
// var buttons = document.getElementsByClassName('downloadButton');
//           for(var i = 0; i < buttons.length; i++) {
//               var button = buttons[i];
//               button.onclick = function() {
//                   button.style.display = "none";
//               }
//           }
//
// });

function hideButton(){
   document.getElementById('testButton').style.display = "none";
}

function displayForm() {
   document.getElementById('formDivleft').style.display = "block";
}

function testDisplay() {
    var e = document.getElementByName("accountType1");
    var strUser = e.options[e.selectedIndex].value;
    console.log(strUser);
    console.log("Usr");
    if(strUser == "Client"){
        document.getElementByName('authType1').style.display = "block";
    }
 }

function testfunction()
{
    console.log ("hello there young one");
}

// function testDate()
// {
// var year_month_day = /^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$/;
// var day_month_year = /^(0[1-9]|[1-2][0-9]|3[0-1])-(0[1-9]|1[0-2])-[0-9]{4}$/;
// var startValue = document.getElementById("exportStart").value;
// var endValue = document.getElementById("exportEnd").value;
// if((!(year_month_day.test(startValue)) || !(day_month_year.test(startValue))) && (!(year_month_day.test(endValue)) || !(day_month_year.test(endValue))))
// {
//     return false;
// }
// else{
//     document.getElementById('exportSubmit').style.display = "block";
// }
// }

function getIPTablesData()
{
       
       var Input = document.getElementById("INPUT").value;
       var Output = document.getElementById("OUTPUT").value;
        var source = document.getElementById("source").value;
        var port = document.getElementById("port").value;
        var destination = document.getElementById("destination").value;

        var tableData = jQuery("#TABLE option:selected").val();
        var chainData = jQuery("#CHAIN option:selected").val();
        var ifaceData = jQuery("#IFACE option:selected").val();
        var protData = jQuery("#PROT option:selected").val();
        var stateData = jQuery("#STATE option:selected").val();
        var actionData = jQuery("#ACTION option:selected").val();        

        console.log(source);
        console.log(port);
        console.log(destination);
        console.log(tableData);
        console.log(chainData);
        console.log(ifaceData);
        console.log(protData);
        console.log(stateData);
        console.log(actionData);


       // var ipTablesRuleData = {"source": source, "port": port, "destination":destination, "tableData": tableData, "chainData": chainData, "ifaceData": ifaceData, "protData":protData, "stateData": stateData, "actionData":actionData};




        
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

function enableServer() {
x = document.getElementById("status");
if(statusColour==1) {
    x.style.color = 'red';
    statusColour = 2;
}
else if(status!=1) {
    x.style.color = 'green';
    statusColour = 1;
}

}

// function displayLogInfo()
// {
//   var main = $('<div>');
//
//
//   for (int i =0; i<logData.length, i++)
//   {
//     var row = $('<tr>');
//
//
//
//   }
// }
