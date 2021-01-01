let changeTableClassName = function () {
    let tables = document.getElementsByTagName("table");
    for (let i=0; i<tables.length; i++) {
        tables[i].className = "table table-bordered table-striped"
    }
};

let getCommentAuthorName = function () {
    let commentAuthors = document.querySelectorAll(".comment-author");
    let authorSet = new Set();
    for (let i=0; i<commentAuthors.length; i++) {
        authorSet.add(commentAuthors[i].innerText);
    }
    let authorList = Array.from(authorSet);
    let result = [];
    for (let i=0; i<authorList.length; i++) {
        let value = {
            key: authorList[i],
            value: authorList[i],
        };
        result.push(value);
    }
    return result;

};

let __main = function () {
    changeTableClassName();
}

__main();