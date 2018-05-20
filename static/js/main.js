var btn = document.getElementById("submit");
var title = document.getElementById("title");
var code = document.getElementById("code");
var language = document.getElementById("language");
var xhr = new XMLHttpRequest();

btn.addEventListener('click', submitCode);
xhr.addEventListener("load", transferComplete);

function copyToClipboard(text){
    var dummy = document.createElement("input");
    document.body.appendChild(dummy);
    dummy.setAttribute('value', text);
    dummy.select();
    document.execCommand("copy");
    document.body.removeChild(dummy);
}

function submitCode()
{
    if (title.value === "")
    {
        alert("Please enter a title!");
        return;
    }

    if (code.value === "")
    {
        alert("Please enter your code!");
        return;
    }

    var lang_input = language.value;
    var title_input = title.value;
    var code_input = code.value;

    xhr.open("POST", "/submit", true);
    xhr.setRequestHeader("Content-type", "text/plain");
    xhr.send('{"language": "' + lang_input + '", "title": "' + title_input + '", "code": "' + code_input + '"}');
}

function transferComplete(evt)
{
    window.location.replace(xhr.responseText)
}