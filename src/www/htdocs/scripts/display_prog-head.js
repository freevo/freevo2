var ob;
var over = false;
var popid;
var popY;

N = (document.all) ? 0 : 1;

function
guide_click(item, event)
{
	var iframe = document.getElementById("hidden");
	iframe.src="proginfo?id=" + item.id;
	document.getElementById("program-waiting").style.display = "";
	document.getElementById("program-info").style.visibility = "hidden";
	var popup = document.getElementById("popup");
	popup.style.display = "";

	w = N ? window.innerWidth : document.body.clientWidth;
	h = N ? window.innerHeight : document.body.clientHeight;

	//alert(event.clientX + "  "  + popup.clientWidth + "  " + w + "  " + h);
	if (event.clientX + popup.clientWidth > w)
		x = (w - popup.clientWidth) - 30;
	else
		x = event.clientX;
	popup.style.left = x + "px";

	page_top = N ? window.pageYOffset : document.body.scrollTop;

	// We can't use popup.clientHeight because it's not valud until
	// after proginfo gets executed, so we guess that it'll be
	// about 175.  Someone else can fix this. :)
	if (event.clientY + 175 > h)
		y = page_top + (h - 175) - 20;
	else
		y = page_top + event.clientY;
	popup.style.top = y + "px";
}

function
program_popup_close()
{
	var popup = document.getElementById("popup");
	popup.style.display = "none";
}

function mouseDown(e) {
  if(over) {
    if(N) {
      ob = document.getElementById(popid);
      X = e.layerX;
      Y = e.layerY;
      return false;
    }
    else {
      ob = document.getElementById(popid);
      ob = ob.style;
      X = event.offsetX;
      Y = event.offsetY;
    }
  }
}

function mouseMove(e) {
  if(ob) {
    if(N) {
      ob.style.top = e.pageY-Y;
      ob.style.left = e.pageX-X;
    }
    else {
      ob.pixelLeft = event.clientX-X + document.body.scrollLeft;
      ob.pixelTop = event.clientY-Y + document.body.scrollTop;
      return false;
    }
  }
}

function mouseUp() {
  ob = null;
}

if(N) {
  document.captureEvents(Event.MOUSEDOWN | Event.MOUSEMOVE | Event.MOUSEUP);
}

document.onmousedown = mouseDown;
document.onmousemove = mouseMove;
document.onmouseup = mouseUp;

