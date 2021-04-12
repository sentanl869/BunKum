const changeTableClassName = () => {
    let tables = document.getElementsByTagName("table")
    for (let i=0; i<tables.length; i++) {
        tables[i].className = "table table-bordered table-striped"
    }
}

const getCommentAuthorName = () => {
    let commentAuthors = document.querySelectorAll(".comment-author")
    let authorSet = new Set()
    for (let i=0; i<commentAuthors.length; i++) {
        authorSet.add(commentAuthors[i].innerText)
    }
    let authorList = Array.from(authorSet)
    let result = []
    authorList.forEach(author => {
        let value = {
            key: author,
            value: author,
        }
        result.push(value)
    })
    return result
}

const __main = () => {
    changeTableClassName()
}

__main()