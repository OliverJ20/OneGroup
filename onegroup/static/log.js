$(document).ready(function(){
    logInfo();
});

//Switch radio Buttons
$(document).on('click.bs.radio', '.btn-radio > .btn', function(e) {
    //Remove active and colour
    $(this).siblings().removeClass('active');
    $(this).siblings().removeClass('btn-success');
    //Add active and colour
    $(this).addClass('active');
    $(this).addClass('btn-success');

    //hide table and switch
    $("#table").fadeOut( function() {
        switch (e.target.id) {
            case "Health":
                healthTable();
                break;
            case "Parking":
                parkingTable();
                break;
            case "Other":
                smokingTable();
                break;
            case "Users":
                usersTable();
                break;
        };
    });
    $("#table").fadeIn(500);
});

//generate Health and Safety table
function healthTable() {
    //set the add button link
    setAddHealth();

    //Set search fields
    searchComboHealth();

    //set title
    $("#title").html("Health and Safety Issues");

    //new table
    var table = $('<table>');

    //Table heading
    var header = $('<tr>');
    header.append($('<th style="text-align: center;">').html("ID"));
    header.append($('<th style="text-align: center;">').html("Date"));
    header.append($('<th style="text-align: center;">').html("Time"));
    header.append($('<th style="text-align: center;">').html("Location"));
    header.append($('<th style="text-align: center;">').html("Violator"));
    header.append($('<th style="text-align: center;">').html("Status"));

    table.append(header);

    //get data
    $.getJSON( "/admin/health/", function( data ) {
        //create row for each issue
        for (var entry in data.issues) {
            var row = $('<tr>').attr("id",data.issues[entry]['Issue_Number']);
            //Link to edit entry
            var link = "/editHealth/"+data.issues[entry]['Issue_Number'];

            row.append($('<td align="center" style="height:30px;">').html('<a href="'+link+'">'+data.issues[entry]['Issue_Number']+'</a>'));
            row.append($('<td align="center">').html(data.issues[entry]['Date']));
            row.append($('<td align="center">').html(data.issues[entry]['Time']));
            row.append($('<td align="center">').html(data.issues[entry]['Place_in_campus']));
            row.append($('<td align="center">').html(data.issues[entry]['Person_Name']));
            table.append(row);
        }
    });

    //Populate and show table
    $("#display").html(table);
};

//generate Parking violation table
function parkingTable() {
    //set the add button link
    setAddReport();

    //Set search fields
    searchComboParking();

    //set title
    $("#title").html("Parking Violations");

    //new table
    var table = $('<table>');

    //Table heading
    var header = $('<tr>');
    header.append($('<th style="text-align: center;">').html("ID"));
    header.append($('<th style="text-align: center;">').html("Date"));
    header.append($('<th style="text-align: center;">').html("Time"));
    header.append($('<th style="text-align: center;">').html("Vehicle License number"));
    header.append($('<th style="text-align: center;">').html("Permit"));
    header.append($('<th style="text-align: center;">').html("Status"));
    table.append(header);

    //get data
    $.getJSON( "/admin/parking/", function( data ) {
        //create row for each issue
        for (var entry in data.issues) {
            var row = $('<tr style="cursor: pointer;bg: ">').attr("id",data.issues[entry]['Citation_Number']);
            var link = "/editParking/"+data.issues[entry]['Citation_Number'];
            row.append($('<td align="center" style="height:30px;">').html('<a href="'+link+'">'+data.issues[entry]['Citation_Number']+'</a>'));
            //row.append($('<td align="center" style="height:30px;">').html(data.issues[entry]['Citation_Number']));
            row.append($('<td align="center">').html(data.issues[entry]['Date']));
            row.append($('<td align="center">').html(data.issues[entry]['Time']));
            row.append($('<td align="center">').html(data.issues[entry]['Vehicle_License_number']));
            if (data.issues[entry]['Permit_Number'] == "None") {
                row.append($('<td align="center">').html("No"));
            } else {
                row.append($('<td align="center">').html("Yes"));
            }
            //Display the payment status of the fine
            if (data.issues[entry]['Status'] == "Pending") {
                //status = "/remindPayment/"+data.issues[entry]['Fine_Number'];
                row.append($('<td align="center">').html('<a href="#" onClick="emailPending('+data.issues[entry]['Fine_Number']+')">'+data.issues[entry]['Status']+'</a>'));
            } else if (data.issues[entry]['Status'] == "Overdue") {
                status = "/overduePayment/"+data.issues[entry]['Fine_Number'];
                row.append($('<td align="center">').html('<a href="#" onClick="emailOverDue('+data.issues[entry]['Fine_Number']+')">'+data.issues[entry]['Status']+'</a>'));
                row.css('background-color','#ffcccc');
            } else {
                row.append($('<td align="center">').html(data.issues[entry]['Status']));
            }
            table.append(row);
        }
    });
    //Populate and show table
    $("#display").html(table);
};

//generate Smoking and other violation table
function smokingTable() {
    //set the add button link
    setAddReport();

    //Set search fields
    searchComboOther();

    //set title
    $("#title").html("Other Violations");

    //new table
    var table = $('<table>');

    //Table heading
    var header = $('<tr>');
    header.append($('<th style="text-align: center;">').html("ID"));
    header.append($('<th style="text-align: center;">').html("Type"));
    header.append($('<th style="text-align: center;">').html("Date"));
    header.append($('<th style="text-align: center;">').html("Time"));
    header.append($('<th style="text-align: center;">').html("Location"));
    header.append($('<th style="text-align: center;">').html("Status"));

    table.append(header);

    //get data
    $.getJSON( "/admin/other/", function( data ) {
        //create row for each issue
        for (var entry in data.issues) {
            var row = $('<tr style="cursor: pointer;">').attr("id",data.issues[entry]['Citation_Number']);
            var link = "/editOther/"+data.issues[entry]['Citation_Number'];
            row.append($('<td align="center" style="height:30px;">').html('<a href="'+link+'">'+data.issues[entry]['Citation_Number']+'</a>'));
            //row.append($('<td align="center" style="height:30px;">').html(data.issues[entry]['Citation_Number']));
            row.append($('<td align="center">').html(data.issues[entry]['Violation_Type']));
            row.append($('<td align="center">').html(data.issues[entry]['Date']));
            row.append($('<td align="center">').html(data.issues[entry]['Time']));
            row.append($('<td align="center">').html(data.issues[entry]['Place_in_campus']));
            if (data.issues[entry]['Status'] == "Pending") {
                row.append($('<td align="center">').html('<a href="#" onClick="emailPending('+data.issues[entry]['Fine_Number']+')">'+data.issues[entry]['Status']+'</a>'));
            } else if (data.issues[entry]['Status'] == "Overdue") {
                row.append($('<td align="center">').html('<a href="#" onClick="emailOverDue('+data.issues[entry]['Fine_Number']+')">'+data.issues[entry]['Status']+'</a>'));
                row.css('background-color','#ffcccc');
            } else {
                row.append($('<td align="center">').html(data.issues[entry]['Status']));
            }
            table.append(row);
        }
    });

    //Populate and show table
    $("#display").html(table);
};

//Generate User table
function usersTable() {
    //disable add button
    setAddUser();

    //Set search fields
    searchComboUsers();

    //set title
    $("#title").html("Users");

    //new table
    var table = $('<table>');

    //Table heading
    var header = $('<tr>');
    header.append($('<th style="width:20px; text-align: center;">').html("ID"));
    header.append($('<th style="width:20px; text-align: center;">').html("Name"));
    header.append($('<th style="width:20px; text-align: center;">').html("Email"));
    header.append($('<th style="width:20px; text-align: center;">').html("Account Type"));

    table.append(header);

    //get data
    $.getJSON( "/admin/users/", function( data ) {
        //create row for each issue
        for (var entry in data.users) {
            var row = $('<tr style="cursor: pointer;">').attr("id",data.users[entry]['User_ID']);
            var link = "/report/"+data.users[entry]['User_ID'];
            row.append($('<td align="center" style="height:30px;">').html('<a href="'+link+'">'+data.users[entry]['User_ID']+'</a>'));
            row.append($('<td align="center">').html(data.users[entry]['Name']));
            row.append($('<td align="center">').html(data.users[entry]['Email']));
            row.append($('<td align="center">').html(data.users[entry]['Account_Type']));
            table.append(row);
        }
    });

    //Populate and show table
    $("#display").html(table);
};

//Send email for pending Fines
function emailPending(id) {
    //Trigger email
    uri = "/remindPayment/"+id;
    $.getJSON(uri, function( data ) {
        if (data.status = "TRUE") {
            alert("A email notification has been sent")
        } else {
            alert("An Error occurred")
        }
    });
}

//Send email for overdue Fines
function emailOverDue(id) {
    //Trigger email
    uri = "/overduePayment/"+id;
    $.getJSON(uri, function( data ) {
        if (data.status = "TRUE") {
            alert("A email notification has been sent")
        } else {
            alert("An Error occurred")
        }
    });
}

function searchComboHealth() {
    var options = {"ID": 0,
      "Date": 1,
      "Time": 2,
      "Location": 3,
      "Violator": 4,
      "Status": 5
    };
    $("#field").empty(); // remove old options
    $.each(options, function(key,value) {
      $("#field").append($("<option></option>")
         .attr("value", value).text(key));
    });
}

function searchComboParking() {
    var options = {"ID": 0,
      "Date": 1,
      "Time": 2,
      "Vehicle License number": 3,
      "Permit": 4,
      "Status": 5
    };

    $("#field").empty(); // remove old options
    $.each(options, function(key,value) {
      $("#field").append($("<option></option>")
         .attr("value", value).text(key));
    });
}

function searchComboOther() {
    var options = {"ID": 0,
      "Type": 1,
      "Date": 2,
      "Time": 3,
      "Location": 4,
      "Status": 5
    };

    $("#field").empty(); // remove old options
    $.each(options, function(key,value) {
      $("#field").append($("<option></option>")
         .attr("value", value).text(key));
    });
}

function searchComboUsers() {
    var options = {"ID": 0,
      "Name": 1,
      "Email": 2,
      "Account Type": 3,
    };

    $("#field").empty(); // remove old options
    $.each(options, function(key,value) {
      $("#field").append($("<option></option>")
         .attr("value", value).text(key));
    });
}

function filter() {
    var field = $("#field").find(":selected").val();
    var value = $("#value").val();

    reset();

    var MyRows = $('#display').find('tbody').find('tr');
    for (var i = 1; i < MyRows.length; i++) {

        if ($(MyRows[i]).find('td:eq('+String(field)+')').text() != String(value)) {
            $(MyRows[i]).hide();
        }
    }
}

function reset(){
    $("#value").val(""); // remove old options
    var MyRows = $('#display').find('tbody').find('tr');
    for (var i = 1; i < MyRows.length; i++) {
        $(MyRows[i]).show();
    }
}

function showTable() {
    $("#table").show(800);
}

function setAddHealth() {
    $("#add").attr("href", "/health/");
}

function setAddReport() {
    $("#add").attr("href", "/report/new");
}

function setAddUser() {
    $("#add").attr("href", "#");
}