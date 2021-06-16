

function initMap() {
	var icon = {
    url: "https://kolyanok.ru/tank.svg", // url
    scaledSize: new google.maps.Size(50, 50), // scaled size
    origin: new google.maps.Point(0,0), // origin
    anchor: new google.maps.Point(35, 35) // anchor
};
  const myLatLng = { lat: -25.363, lng: 131.044 };
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 18,
    center: myLatLng,
  });
  marker = new google.maps.Marker({
    position: myLatLng,
    map,
    title: "Tank",
    icon: icon,
  });
}
const socket = io('http://kolyanok.ru:5001')
		
		    socket.on('connect', () => {
		      console.log("socket connected");
		      document.getElementById('connection').innerHTML="Connected"
		      document.getElementById('statusbar').className="statusbar green-gardinet"
		    });
		    socket.on('disconnect', () => {
		      console.log("socket disconnected");
		      document.getElementById('connection').innerHTML="Disconnected"
		      document.getElementById('statusbar').className="statusbar red-gardinet"
		    });
		    socket.on("battery", function(battery){ 
		    		document.getElementById('battery-pv').innerHTML=battery.percentage+"% ("+battery.voltage+"v)"
		    		document.getElementById('batteryLevel').style="width: "+battery.percentage+"%;"
		    });
		    socket.on("wifi", function(wifi){
		    		document.getElementById('wifisignal').className="waveStrength-"+Math.round(parseInt(wifi.signal)/25)
		    });
		    socket.on("modem", function(modem){
		    		document.getElementById('modemsignal').className="signal-bars mt1 sizing-box good bars-"+modem.signal
		    		document.getElementById('nettype').innerHTML=modem.nettype
		    });
		    socket.on("gps", function(gps){
		    		if (gps.sattelites>0)
		    		{
		    			document.getElementById('gps-icon').className="gps-icon active-gps";
		    		}
		    		else
		    		{
		    			document.getElementById('gps-icon').className="gps-icon inactive-gps";
		    		}
		    		document.getElementById('gps-sattelites').innerHTML=gps.sattelites
		    		if (gps.speed == 'N/A')
		    		{
		    			document.getElementById('speed').innerHTML=gps.speed=''
		    		}
		    		else
		    		{
		    			document.getElementById('speed').innerHTML=parseInt(gps.speed)+" km/h"
		    	  }
		    	  if (gps.latitude != 'N/A' && gps.longitude != 'N/A')
		    	  {
		    	  	document.getElementById('gps-link').className='gps-link';
		    	  	position = new google.maps.LatLng(gps.latitude, gps.longitude)
		    	  	marker.setPosition (position)
		    	  	map.setCenter (position)
		    	  }
		    });
		    socket.on("scan", function(scan){
		    	
		    	table = document.getElementById('wifinetworks')
		    	table.innerHTML='';
		    	scan.forEach(function(entry) {
		    	el = document.createElement('tr')
		    	table.appendChild(el)
		    	signal = document.createElement('td')
		    	if(entry.signal <= -100)
		    	{quality = 0;}
    			else if(entry.signal >= -50)
    				{
        quality = 100;
      }
    			else
    				{
        quality = 2 * (entry.signal + 100);
      }
      
		    	signal.innerHTML='<div id="table-wifisignal" class="waveStrength-'+Math.round(parseInt(quality)/25)+'"><div class="wv4 wave"><div class="wv3 wave"><div class="wv2 wave"><div class="wv1 wave"></div></div></div></div></div>'
		    	el.appendChild(signal)
		    	ssid = document.createElement('td')
		    	ssid.innerHTML=entry.ssid
		    	el.appendChild(ssid)
		    	encrypted = document.createElement('td')
		    	encrypted.innerHTML=entry.encrypted?'Yes':'No'
		    	el.appendChild(encrypted)
		    	connect = document.createElement('td')
		    	connect.innerHTML = '<button type="button" class="btn btn-primary">Connect</button>'
		    	el.appendChild(connect)
		    	});
		    });
		    socket.onAny((event, ...args) => {
  				console.log(event, args);
				});
		    document.addEventListener('keydown', function (event) {
		    	if (event.repeat) { return }
		        if (event.keyCode === 87) { //w
		            socket.emit('message', 'w');
		        }
		        if (event.keyCode === 65) { //a
		            socket.emit('message', 'a');
		
		        }
		         if (event.keyCode === 83) { //s
		           socket.emit('message', 's');
		
		        }
		        if (event.keyCode === 68) { //d
		            socket.emit('message', 'd');
		
		        }
		        if (event.keyCode === 38) { //w
		            socket.emit('message', 'w');
		        }
		        if (event.keyCode === 37) { //a
		            socket.emit('message', 'a');
		
		        }
		         if (event.keyCode === 40) { //s
		           socket.emit('message', 's');
		
		        }
		        if (event.keyCode === 39) { //d
		            socket.emit('message', 'd');
		
		        }
		});
		
		document.addEventListener('keyup', function (event) {
		        if (event.keyCode === 87 || event.keyCode === 65 || event.keyCode === 83 || event.keyCode === 68 || ( event.keyCode >36 &&  event.keyCode < 41)) { //w
		            socket.emit('message', '/');
		        }
		});
		function isTouchDevice() {
  return (('ontouchstart' in window) ||
     (navigator.maxTouchPoints > 0) ||
     (navigator.msMaxTouchPoints > 0));
		}
		window.addEventListener("gamepadconnected", function(e) {
			joy1Y=0;
			joy2Y=0;
			setInterval(function(){var gamepad = navigator.getGamepads()[0]; j1 = parseInt(gamepad.axes[1]*-50); if (Math.abs(j1)<3) { j1=0; } if (j1!=joy1Y) {socket.emit('left', j1); joy1Y=j1; }}, 5);
			setInterval(function(){var gamepad = navigator.getGamepads()[0]; j2 = parseInt(gamepad.axes[3]*-50); if (Math.abs(j2)<3) { j2=0; } if (j2!=joy2Y) {socket.emit('right', j2); joy2Y=j2}}, 5);
		});
		$(function(){
    $('#full-width').draggable({
      handle: ".modal-header"
  });
    $('#full-width').resizable();
  
});

$(function(){
    $('#full-width-wifi').draggable({
      handle: ".modal-header"
  });
    $('#full-width-wifi').resizable();
  
});