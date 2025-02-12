///<reference path="utils.ts"/>
// @ts-nocheck

let tabs = ["Net worth", "Name search", "Hex search", "Leaderboard"];
let activeTab = "";
function preLoad() {
  let tabStr = "";
  let i=0;
  for (let e of document.getElementsByClassName("tab")) {
    tabStr += `
      <a href="#${e.id}" class="tabtop blu fssml" onclick="setTab('${e.id}'); return false;" id='t-${e.id}'>
        ${tabs[i]}
      </a>
    `
    i++;
  }
  byId("tabctn").innerHTML = tabStr;
  setTab(docURL.hash.slice(1));
}

function nameSearch() {
  let name = byId("inp-shipname").value; 
  send(JSON.stringify({action:"strawbCmd", data:{cmd:"NameSearch", val:name}}), (res)=>{
    let value = JSON.parse(res.data.output);
    if (value.entries == null) alertDialog("Error in search, check console.");
    else {
      console.log(value);
      byId("resCtn2").style.display = "block";
      byId("resct").innerText = value.entries + " result"+pluralise(value.entries);
      let outputCtn = byId("resCtn2").querySelector(".breakdown");
      outputCtn.innerHTML = "";
      dispShipSummary(outputCtn, value.ships);
      scrollToID("resCtn2");
    }
  });
}

function hexSearch() {
  let name = byId("inp-hex").value; 
  send(JSON.stringify({action:"strawbCmd", data:{cmd:"byHex", val:name}}), (res)=>{
    let value = JSON.parse(res.data.output);
    if (value.shipData == null) {
      ephemeralDialog("Hex code not found.");
      byId("resCtn4").style.display = "block";
      byId("resCtn4").innerHTML = "<b class='red nohover nooutline'>No results found.</b>"
    }
    else {
      console.log(value);
      byId("resCtn4").style.display = "block";
      // byId("resct").innerText = value.entries + " result"+pluralise(value.entries);
      let outputCtn = byId("resCtn4")
      outputCtn.innerHTML = "";
      dispShipSummary(outputCtn, [value]);
      scrollToID("resCtn4");
    }
  });
}

function dispShipSummary(outputCtn:HTMLElement, ships:any) {
  for (let ship of ships) {
    let shipData = ship.shipData;
    outputCtn.innerHTML += `
    <div class="entry">
      <div class="left">

      </div>
      <div class="right">
        <b class="nowrap fssml">${shipData.name}</b> <p class="nowrap fssml">{${shipData.hex}}</p><br>
        <b class="blu nohover nowrap">Calculated value:</b> <h2 class="nowrap" style="margin-left: 0px">${shipData.value != null?Number(shipData.value).toLocaleString('en-US'):"Unknown"} flux
        (#${Number(ship.rank).toLocaleString('en-US')})</h2><br>
      </div>
    </div>
    `
  }
}

function pluralise(v:number) {
  return v==1?"":"s";
}

function setTab(id) {
  if (!id || byId(id) == null || byId("t-"+id) == null) id = "networth";
  if (byId(activeTab) != null) {
    byId(activeTab).classList.remove("active");
    byId("t-"+activeTab).classList.remove("active");
  }
  document.location = "#"+id;
  byId(id).classList.add("active");
  byId("t-"+id).classList.add("active");
  activeTab = id;
}


let errSrc = 'https://cdn.glitch.global/e26d8c22-78e4-40e9-ba1f-e1cc7c1ae3d3/7f1ebdbe-2bdd-4e69-8912-55f1c26c2f11.ezgif-39bec930550f86.png?v=1739037368902';
function calcWorth() {
  let area = byId("area") as HTMLTextAreaElement;
  let out = byId("out") as HTMLTextAreaElement;
  send(JSON.stringify({action:"strawbCmd", data:{cmd:"ValueTotal", shiplist:area.value}}), (res)=>{
    let output = JSON.parse(res.data.output);
    
    let initMatch = output.value;
    if (initMatch == null) alertDialog("Invalid shiplist data.", ()=>{});
    else {
      byId("resCtn").style.display = "block";
      let breakdownEle = byId("breakdown") as HTMLDivElement;
      breakdownEle.innerText = "";
      byId("summary").innerText = Number(output.value).toLocaleString('en-US') +" flux.";
      byId("date").innerText = "This includes updates until: "+output.date;
      // # name hex worth rank loadtime icon
      for (let shipData of output.shipData) {
        breakdownEle.innerHTML += 
        `<div class="entry">
          <div class="left">
            <img src="${shipData.icon}" onerror="if (this.src != errSrc) this.src = errSrc"/>
          </div>
          <div class="right">
            <b class="nowrap">${shipData.name}</b> <p class="nowrap">{${shipData.hex_code}}</p><br>
            <b class="fssml nowrap">Calculated value:</b> <h2 class="nowrap" style="margin-left: 0px">${shipData.shipworth != null?Number(shipData.shipworth).toLocaleString('en-US'):"Unknown"} flu
            <b class="fssml nowrap">Calculated value:</b> <h2 class="nowrap" style="margin-left: 0px">${shipData.shipworth != null?Number(shipData.shipworth).toLocaleString('en-US'):"Unknown"} flux
            (#${Number(shipData.placement).toLocaleString('en-US')})</h2><br>
            <p>Last loaded: ${shipData.load_time}</p>
          </div>
        </div>`
      }
      scrollToID("resCtn");
      ephemeralDialog("Success!")
    }
  });
}

let page = 1;
function getLeaderboard(delta:number) {
  if (delta == 0) page = Number(byId("inp-page").value);
  else page += delta;
  if (page < 1) page = 1; 
  byId("inp-page").value = page;
  send(JSON.stringify({action:"strawbCmd", data:{cmd:"leaderboard", val:page-1}}), (res)=>{
    let output = JSON.parse(res.data.output);
    let parentCtn = byId("resCtn3");
    parentCtn.style.display = "block";
    let outputCtn = parentCtn.querySelector(".breakdown");
    byId("pagenum").innerText = "Page "+(page);
    outputCtn.innerHTML = "";
    dispShipSummary(outputCtn, output.ships);
    scrollToID("resCtn3");
  })
}
