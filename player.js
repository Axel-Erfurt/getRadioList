(function filterlist() {

  var options = {
    valueNames: ["chlist"]
  }

  var listObj = new List("test", options);
}())

var myaudio;
var playlist;
var tracks;
var current;

initaudio();
function initaudio(){
    current = 0;
    myaudio = $('#audio');
    playlist = $('#playlist');
    tracks = playlist.find('li a');
    len = tracks.length - 1;
    myaudio[0].volume = .90;
    myaudio[0].play();
    playlist.find('a').click(function(e){
        e.preventDefault();
        link = $(this);
        current = link.parent().index();
        runaudio(link, myaudio[0]);
    });
    myaudio[0].addEventListener('ended',function(e){
        current++;
        if(current == len){
            current = 0;
            link = playlist.find('a')[0];
        }else{
            link = playlist.find('a')[current];
        }
        runaudio($(link),myaudio[0]);
    });
}
// Se cambió esta parte del código para que la función encuentre la segunda URL a través del atributo data-altsrc
function runaudio(link, player){
    $(player).find('#primarysrc').attr('src', link.attr('href'));
    $(player).find('#secondarysrc').attr('src', link.attr('data-altsrc'));
    par = link.parent();
    par.addClass('active').siblings().removeClass('active');
    myaudio.load();
}
