window.onload = (function(){
    this.console.log("hello");
    document.getElementById('silverCB').onchange = function() {
        document.getElementById('silverQC').disabled = !this.checked;
        console.log("bye");
    }
});