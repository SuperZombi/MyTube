var origin = "http://192.168.1.104"
load_icon()

window.onload=_=>{
	load_sidebar()
	buildBreadcrumbs()
	initDataTypesLinks()
	initLinkerCopy()
	if (window.location.hash){
		document.getElementById(window.location.hash.split("#").at(-1)).scrollIntoView();
	}
}

function load_icon(){
	let url = new URL("data/images/icon.png", origin)
	let link = document.createElement('link');
	link.rel = 'icon';
	link.href = url
	document.head.appendChild(link);
}


function load_sidebar() {
	let url = new URL("data/htmls/sidebar.html", origin)
	let current_url = window.location.pathname.toLowerCase().split(".html")[0]
	fetch(url.href).then(res=>{if (res.ok){return res.text()}}).then(data=>{
		if (!data){return}
		let string = data.replace(/\${(.*?)\}/g, (match, contents)=>{ return eval(contents) })
		document.querySelector(".sidebar").innerHTML = string
		let current = document.querySelector(`.sidebar a[href="${origin + current_url}"]`)
		if (current){
			current.removeAttribute("href")
			current.classList.add("selected")
			let details = current.closest("details")
			if (details){details.open = true}
		}
	})
}


function buildBreadcrumbs(){
	let breadcrumbs = document.querySelector(".breadcrumbs")
	if (!breadcrumbs){return}
	let relativeUrl = window.location.pathname.replace(origin, '')
	let path = relativeUrl.split('/').filter(Boolean)
	
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

function initDataTypesLinks(){
	let typesUrls = {
		"int": "https://docs.python.org/3/library/functions.html#int",
		"str": "https://docs.python.org/3/library/stdtypes.html#str",
		"datetime": "https://docs.python.org/3/library/datetime.html#datetime.datetime"
	}
	document.querySelectorAll("a.type").forEach(el=>{
		let url = typesUrls[el.innerText]
		if (url){
			el.href = url
			el.target = "_blank"
		}
	})
}
function initLinkerCopy(){
	document.querySelectorAll(".linker").forEach(el=>{
		el.onclick = _=>{copyText(el.href)}
		el.title = "Copy link"
	})
}
function copyText(text) {
	const textArea = document.createElement("textarea");
	textArea.value = text;
	document.body.appendChild(textArea);
	textArea.select();
	document.execCommand('copy');
	document.body.removeChild(textArea);
}
