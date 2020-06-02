<!-- read patient results file from server -->
function readResults(filename,elementId){
	jQuery.get('readResults.cgi',{filename:filename},
	function(data){
		jQuery(elementId).html(data);
	});
}

function compareAlignment(filename,header){
	var form = document.createElement("form");
		form.setAttribute("method", "post");
		form.setAttribute("action", "compareAlignment.cgi");
		form.setAttribute("target", "_blank");

	var hiddenField = document.createElement("input");              
		hiddenField.setAttribute("visible","hidden");
		hiddenField.setAttribute("name","filename");
		hiddenField.setAttribute("value",filename);
		form.appendChild(hiddenField);

	var hiddenField2 = document.createElement("input");
		hiddenField2.setAttribute("visible","hidden");
		hiddenField2.setAttribute("name","header");
		hiddenField2.setAttribute("value",header);
		form.appendChild(hiddenField2);
		document.body.appendChild(form);
		form.submit();
}
