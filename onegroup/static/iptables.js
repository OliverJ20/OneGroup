





function getIPTablesData()
{
       
       var source = document.getElementById("source");
        var port = document.getElementById("port");
        var destination = document.getElementById("destination"); 

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
        
}
