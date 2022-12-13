/*function deleteNote(noteId){
    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId}),
    }).then((_res) => {
        window.location.href = "/";
    });
}*/

function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }

function Openform(){
  document.getElementById('form1').style.display = 'block';
}

function CloseForm(){
  document.getElementById('form1').style.display = 'none';
}

var counter = 1;
    setInterval(function () {
      document.getElementById('radio' + counter).checked = true;
      counter++;
      if (counter > 4) {
        counter = 1;
      }
    }, 5000);

function RemoveRow(){
  var td = event.target.parentNode;
  var tr = td.parentNode;
  tr.parentNode.removeChild(tr);
}

function OpenForm2(){
  document.getElementById('form2').style.display = 'block';
}

function CloseForm2(){
  document.getElementById('form2').style.display = 'none';
}