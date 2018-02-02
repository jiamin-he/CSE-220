// When the user clicks on the browser action icon.
chrome.browserAction.onClicked.addListener(function(tab) {
  //Look to see if the extension page is open already and if not, open it.

  var optionsUrl = chrome.extension.getURL('index.html');

  chrome.tabs.query({}, function(extensionTabs) {
    var found = false;

    for (var i = 0; i < extensionTabs.length; i++) {
      if (optionsUrl == extensionTabs[i].url) {
        found = true;
        console.log("tab id: " + extensionTabs[i].id);
        chrome.tabs.update(extensionTabs[i].id, {
          "selected": true
        });
      }
    }

    if (found == false) {
      chrome.tabs.create({
        url: "index.html"
      });
    }
  });
});

function install_notice() {
    if (localStorage.getItem('install_time'))
        return;

    var now = new Date().getTime();
    localStorage.setItem('install_time', now);
    chrome.tabs.create({url: "index.html"});
    console.log("installation");
}
install_notice();

chrome.alarms.create("check-last-upload", {
  when: 0,
  periodInMinutes: 30
});

chrome.alarms.onAlarm.addListener(function(alarm) {
  chrome.storage.local.get({
    'lastPdkUpload': 0
  }, function(result) {
    var lastUpload = 0;

    if (result.lastPdkUpload != undefined)
      lastUpload = Number(result.lastPdkUpload);

    var svyEndData = localStorage.getItem('svyEnd');
    var svyEndObj = JSON.parse(svyEndData);
    var svyEnd = null;
    if (svyEndObj !== null) {
      svyEnd = svyEndObj[0].endType;
    }

    console.log("survey end status: " + svyEnd);

    var now = new Date();

    if (lastUpload === 0 && svyEnd !== 0) {
      chrome.browserAction.setBadgeText({
        text: "1"
      });
      chrome.browserAction.setBadgeBackgroundColor({
        color: "#FF0000"
      });
      chrome.browserAction.setTitle({
        title: "Participate in our research project! Open this extension and click the cloud icon."
      });
      console.log("has not uploaded");
    } else if (lastUpload !== 0 && svyEnd === null) {
      chrome.browserAction.setBadgeText({
        text: "1"
      });
      chrome.browserAction.setBadgeBackgroundColor({
        color: "#FF0000"
      });
      chrome.browserAction.setTitle({
        title: "Please finish our survey! Click here to see the link to your survey."
      });
      console.log("uploaded, didn't finish survey!!");
    } else if (now.getTime() - lastUpload > (1000 * 60 * 60 * 1440) && svyEnd !== 0) // 60 days (in hours)
    {
      chrome.browserAction.setBadgeText({
        text: "1"
      });
      chrome.browserAction.setBadgeBackgroundColor({
        color: "#FF0000"
      });

      chrome.browserAction.setTitle({
        title: "Upload additional browsing data! Click the cloud upload icon in the app."
      });
    } else if(svyEnd===1 && now.getTime() - lastUpload < (1000 * 60 * 60 * 1440)){
      chrome.browserAction.setIcon({
        path: "images/star-yellow-64.png"
      });

      chrome.browserAction.setTitle({
        title: "Web Historian"
      });
    }
    else {
      chrome.browserAction.setIcon({
        path: "images/star-yellow-64.png"
      });

      chrome.browserAction.setTitle({
        title: "Web Historian"
      });
      console.log("Uploaded less tha 60 days ago or not eligible or did not consent");
    }
  });
});
