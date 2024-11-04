var origin = "https://superzombi.github.io/MyTube"

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
	initCodeExection()
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
		a.innerHTML = name.replaceAll("_", " ")
		li.appendChild(a)
		breadcrumbs.appendChild(li)
	}
	makeLi("docs", origin)
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
		"bool": "https://docs.python.org/3/library/functions.html#bool",
		"list": "https://docs.python.org/3/library/stdtypes.html#list",
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

const sleep = ms => new Promise(res=>setTimeout(res,ms))
function initCodeExection(){
	document.querySelectorAll(".execute").forEach(details=>{
		let area = details.querySelector("pre")
		let code = details.querySelector("pre code")
		let lines = code.innerHTML.split("\n")
		let timeout = lines.length > 10 ? 25 : 50;
		details.addEventListener("toggle", async ()=>{
			code.innerHTML = ""
			if (details.open){
				area.scrollIntoView({block: "center", behavior: "smooth"});
				await sleep(1000);
				for (let i=0; i<lines.length;i++){
					code.innerHTML += lines[i]
					if (i != lines.length - 1){
						code.innerHTML += "\n"
					}
					area.scrollIntoView({block: "center"});
					await sleep(timeout);
				}
			}
		})
	})
}
