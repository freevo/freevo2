var ob;
var over = false;
var popid;
var popY;

N = (document.all) ? 0 : 1;

function focusPop(pop) {
  popid = pop;
  over = true;
}

function unfocusPop(pop) {
  popid = '';
  over = false;
}

function showPop(pop, cell) {
  pop = document.getElementById(pop);
  pop.style.top = popY-100;
  pop.style.visibility = 'visible';
}

function closePop(pop) {
  pop = document.getElementById(pop);
  pop.style.visibility = 'hidden';
}

function mouseDown(e) {
  popY = e.pageY;
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

