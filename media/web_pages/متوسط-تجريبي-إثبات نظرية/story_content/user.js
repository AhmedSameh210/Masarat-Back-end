window.InitUserScripts = function()
{
var player = GetPlayer();
var object = player.object;
var addToTimeline = player.addToTimeline;
var setVar = player.SetVar;
var getVar = player.GetVar;
window.Script1 = function()
{
  DS.appState.setVolume(1);//play sound


}

window.Script2 = function()
{
  DS.appState.setVolume(0); //mute 

}

};
