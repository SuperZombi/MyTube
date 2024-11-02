window.onload=_=>{
	var origin = "http://192.168.1.104/"
	load_sidebar()
	buildBreadcrumbs()
}


function load_sidebar() {
	let url = new URL("htmls/sidebar.html", origin)
	fetch(url.href).then(res=>res.text()).then(data=>{
		let string = data.replace(/\${(.*?)\}/g, (match, contents)=>{ return eval(contents) })
		document.querySelector(".sidebar").innerHTML = string
		let current = document.querySelector(`.sidebar a[href="${origin + window.location.pathname}"]`)
		if (current){
			current.removeAttribute("href")
			current.classList.add("selected")
		}
	})
}


function buildBreadcrumbs(){
	let relativeUrl = window.location.pathname.replace(origin, '')
	let path = relativeUrl.split('/').filter(Boolean)

	let breadcrumbs = document.querySelector(".breadcrumbs")
	function makeLi(name, url){
		let li = document.createElement("li")
		let a = document.createElement("a")
		if (url){a.href = url}
		a.innerHTML = name
		li.appendChild(a)
		breadcrumbs.appendChild(li)
	}
	makeLi("Docs", origin)
	for (let i=0; i<path.length;i++){
		let origin_url = origin + "/" + path[i]
		if (i == path.length -1){
			origin_url = ""
		}
		makeLi(path[i], origin_url)
	}
}
