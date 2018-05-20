var btn = document.getElementById("submit");
var copy = document.getElementById("copy");
var title = document.getElementById("title");
var language = document.getElementById("language");
var xhr = new XMLHttpRequest();

btn.addEventListener('click', submitCode);
xhr.addEventListener("load", transferComplete);

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