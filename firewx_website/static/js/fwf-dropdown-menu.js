function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
  }
  
  // Close the dropdown if the user clicks outside of it
  window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
  }

  window.onload = function() {
    makeplots(json_fwf_ca32);

    // fwfTimeLayers(topo_file, 'styler15')
  };


function selectRegion() {
  var selectBox = document.getElementById("selectBox");
  console.log(selectBox);

  var value = selectBox.options[selectBox.selectedIndex].value;
  console.log(value);
  if (value =="Canada Wide 32 km"){
    var note = "Canada Wide 32 km";
    console.log(note);
    map.removeLayer(fwflocation);
    map.flyTo([53.684414, -98.44137],3);
    makeplots(json_fwf_ca32);
  }
  else if (value=="Canada Wide 16 km") {
    var note = "Canada Wide 16 km";
    console.log(note);
    map.removeLayer(fwflocation);
    map.flyTo([53.684414, -98.44137],3);
    makeplots(json_fwf_ca16);
  }
  else if (value=="British Columbia 4 km") {
    var note = "British Columbia 4 km";
    console.log(note);
    map.removeLayer(fwflocation);
    map.flyTo([52.319,  -124.2],5);
    makeplots(json_fwf_bc4);

  }
  else {
    
  }
};
