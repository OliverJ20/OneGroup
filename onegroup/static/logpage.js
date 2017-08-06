/**
 * Created by Oliver on 8/6/2017.
 */

$(document).ready(function () {
    addInfo();

})

function addInfo()
{
  $.get("/logtestdata/", function (data)
    {


       var LogInfo = data;
      // var logStringArray = ["friday 12:00pm server hacked","monday 12:00pm server hacked", "thursday 2:00pm server hacked", "sunday 1:00pm nerd" ];



        var main = $('<div class = "tableScroll">');
        var table = $('<table>');
        var header = $('<tr>');
        //header.append($('<th style="width:auto;white-space:nowrap;">'));
         header.append($('<th style="width:auto;white-space:nowrap;">').html("Log report "));
        table.append(header);
        console.log(LogInfo);
         console.log(LogInfo["logData"][0]);
        console.log(LogInfo["logData"].length);
        for (var i = 0; i<LogInfo["logData"].length; i++)
        {
            var row = $('<tr>');
            row.append($('<td style="width:auto;white-space:nowrap;text-align:right;" ">').html(LogInfo["logData"][i]));
            console.log(LogInfo["logData"][i])
            //var cell = $('<td style="width:auto;white-space:nowrap;text-align:center;" >');
           // cell.html("hello");
           // row.append(cell);
            table.append(row);

        }

        main.append(table);
        var mainhtml = main.html();
        $('#logTable').html(mainhtml);

      // var logInfo = $('<p>').html(logInfo[0]);
      // div.append(div);
      // div.append(logInfo);
      // $('#FrontLogInfo').html(div.html());

    })
}