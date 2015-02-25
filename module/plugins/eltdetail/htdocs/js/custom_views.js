/*Copyright (C) 2009-2011 :
     Gabes Jean, naparuba@gmail.com
     Gerhard Lausser, Gerhard.Lausser@consol.de
     Gregory Starck, g.starck@gmail.com
     Hartmut Goebel, h.goebel@goebel-consult.de
     Andreas Karfusehr, andreas@karfusehr.de

 This file is part of Shinken.

 Shinken is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Shinken is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with Shinken.  If not, see <http://www.gnu.org/licenses/>.
*/


var _already_loaded = {};

// when we show a custom view tab, we lazy load it :D
function show_custom_view(p){
	// console.log('Show', p)
	var hname = p.attr('data-elt-name');
	var cvname = p.attr('data-cv-name');

	if (cvname in _already_loaded){
		return;
	}

	var _t = new Date().getTime();
	var spinner = get_spinner('cv'+cvname);
	$('#cv'+cvname).load('/cv/'+cvname+'/'+hname+"?_="+_t, function(response, status, xhr) {
		if (status == "error") {
			var msg = "Sorry but there was an error: ";
			$('#cv'+cvname).html(msg + xhr.status + " " + xhr.statusText);
			// $('#cv'+cvname).remove();
			// $('#tab-cv-'+cvname).remove();
		}
	});

	_already_loaded[cvname] = true;
}

// When we show the custom view tab, we lazy load the view ...
$(window).ready(function(){
	$('.cv_pane').on('shown.bs.tab', function (e) {
		show_custom_view($(this));
	})

	// And for each already active on boot, show them directly!
	$('.cv_pane').each(function(index, elt ) {
		show_custom_view($(elt));
	});
});


function reload_custom_view(name){
	// Be sure to remove the panel from already loaded panels, else it won't load
	delete _already_loaded[name];
	show_custom_view($('#tab-cv-'+name));
}