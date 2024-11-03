var origin = "https://superzombi.github.io/MyTube"
load_icon()

window.onload=_=>{
	load_sidebar()
	buildBreadcrumbs()
	initDataTypesLinks()
	initLinkerCopy()
	initCodeCopy()
	if (window.location.hash){
		scrollToHash()
	}
	window.addEventListener("hashchange", _=>{ scrollToHash() });
}

function scrollToHash(){
	let target = document.getElementById(window.location.hash.split("#").at(-1))
	if (target){
		let elementPosition = target.getBoundingClientRect().top;
		let offsetPosition = elementPosition
		if (target.querySelector("pre")){
			offsetPosition = elementPosition - target.offsetHeight;	
		}
		document.querySelector(".content").scrollBy({top: offsetPosition});
	}
}

function relativePath(){
	let href = window.location.origin+window.location.pathname.toLocaleLowerCase()
	return href.replace(origin.toLocaleLowerCase(), '')
}

function load_icon(){
	let url = new URL("data/images/icon.png", `${origin}/`)
	let link = document.createElement('link');
	link.rel = 'icon';
	link.href = url
	document.head.appendChild(link);
}


function load_sidebar() {
	let url = new URL("data/htmls/sidebar.html", `${origin}/`)
	let current_url = relativePath().split("index.html")[0]
	fetch(url.href).then(res=>{if (res.ok){return res.text()}}).then(data=>{
		if (!data){return}
		let string = data.replace(/\${(.*?)\}/g, (match, contents)=>{ return eval(contents) })
		document.querySelector(".sidebar").innerHTML = string
		document.querySelector("#menuToggle").onclick = _=>{
			document.querySelector(".sidebar").classList.toggle("open")
		}
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
	let path = relativePath().split('/').filter(Boolean)
	
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
function initCodeCopy(){
	function wrap(el) {
		let wrapper = document.createElement("div")
		el.parentNode.insertBefore(wrapper, el);
		wrapper.appendChild(el);
	}
	document.querySelectorAll("pre.code").forEach(el=>{
		let span = document.createElement("button")
		span.classList.add("copy-code")
		el.appendChild(span)
		if (el.clientHeight > 70){
			span.classList.add("pined")
		}
		wrap(el)
		span.title = "Copy code"
		span.onclick = _=>{
			let text = el.querySelector("code").innerText.replaceAll("	", "    ")
			copyText(text)
		}
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
