let changeTableClassName = function () {
    let tables = document.getElementsByTagName("table")
    for (let i=0; i<tables.length; i++) {
        tables[i].className = "table table-bordered table-striped"
    }
}

let __main = function () {
    changeTableClassName()
}

__main()