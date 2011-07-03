if (!window['google']) {
window['google'] = {};
}
if (!window['google']['loader']) {
window['google']['loader'] = {};
google.loader.ServiceBase = 'http://www.google.com/uds';
google.loader.GoogleApisBase = 'http://ajax.googleapis.com/ajax';
google.loader.ApiKey = 'notsupplied';
google.loader.KeyVerified = true;
google.loader.LoadFailure = false;
google.loader.Secure = false;
google.loader.GoogleLocale = 'www.google.com';
google.loader.ClientLocation = {"latitude":55.95,"longitude":-3.2,"address":{"city":"Edinburgh","region":"Lanarkshire","country":"United Kingdom","country_code":"GB"}};
google.loader.AdditionalParams = '';
(function() {var d=true,g=null,h=false,j=encodeURIComponent,l=window,n=undefined,o=document;function p(a,b){return a.load=b}var q="push",r="replace",s="charAt",t="ServiceBase",u="name",v="getTime",w="length",x="prototype",y="setTimeout",z="loader",A="substring",B="join",C="toLowerCase";function D(a){if(a in E)return E[a];return E[a]=navigator.userAgent[C]().indexOf(a)!=-1}var E={};function F(a,b){var c=function(){};c.prototype=b[x];a.T=b[x];a.prototype=new c}
function G(a,b){var c=a.H||[];c=c.concat(Array[x].slice.call(arguments,2));if(typeof a.u!="undefined")b=a.u;if(typeof a.t!="undefined")a=a.t;var e=function(){var f=c.concat(Array[x].slice.call(arguments));return a.apply(b,f)};e.H=c;e.u=b;e.t=a;return e}function H(a){a=Error(a);a.toString=function(){return this.message};return a}function I(a,b){for(var c=a.split(/\./),e=l,f=0;f<c[w]-1;f++){e[c[f]]||(e[c[f]]={});e=e[c[f]]}e[c[c[w]-1]]=b}function J(a,b,c){a[b]=c}if(!K)var K=I;if(!L)var L=J;google[z].v={};K("google.loader.callbacks",google[z].v);var M={},N={};google[z].eval={};K("google.loader.eval",google[z].eval);
p(google,function(a,b,c){function e(k){var m=k.split(".");if(m[w]>2)throw H("Module: '"+k+"' not found!");else if(typeof m[1]!="undefined"){f=m[0];c.packages=c.packages||[];c.packages[q](m[1])}}var f=a;c=c||{};if(a instanceof Array||a&&typeof a=="object"&&typeof a[B]=="function"&&typeof a.reverse=="function")for(var i=0;i<a[w];i++)e(a[i]);else e(a);if(a=M[":"+f]){if(c&&!c.language&&c.locale)c.language=c.locale;if(c&&typeof c.callback=="string"){i=c.callback;if(i.match(/^[[\]A-Za-z0-9._]+$/)){i=l.eval(i);
c.callback=i}}if((i=c&&c.callback!=g)&&!a.s(b))throw H("Module: '"+f+"' must be loaded before DOM onLoad!");else if(i)a.m(b,c)?l[y](c.callback,0):a.load(b,c);else a.m(b,c)||a.load(b,c)}else throw H("Module: '"+f+"' not found!");});K("google.load",google.load);
google.S=function(a,b){if(b){if(O[w]==0){P(l,"load",Q);if(!D("msie")&&!(D("safari")||D("konqueror"))&&D("mozilla")||l.opera)l.addEventListener("DOMContentLoaded",Q,h);else if(D("msie"))o.write("<script defer onreadystatechange='google.loader.domReady()' src=//:><\/script>");else(D("safari")||D("konqueror"))&&l[y](S,10)}O[q](a)}else P(l,"load",a)};K("google.setOnLoadCallback",google.S);
function P(a,b,c){if(a.addEventListener)a.addEventListener(b,c,h);else if(a.attachEvent)a.attachEvent("on"+b,c);else{var e=a["on"+b];a["on"+b]=e!=g?aa([c,e]):c}}function aa(a){return function(){for(var b=0;b<a[w];b++)a[b]()}}var O=[];google[z].N=function(){var a=l.event.srcElement;if(a.readyState=="complete"){a.onreadystatechange=g;a.parentNode.removeChild(a);Q()}};K("google.loader.domReady",google[z].N);var ba={loaded:d,complete:d};function S(){if(ba[o.readyState])Q();else O[w]>0&&l[y](S,10)}
function Q(){for(var a=0;a<O[w];a++)O[a]();O.length=0}
google[z].d=function(a,b,c){if(c){var e;if(a=="script"){e=o.createElement("script");e.type="text/javascript";e.src=b}else if(a=="css"){e=o.createElement("link");e.type="text/css";e.href=b;e.rel="stylesheet"}(a=o.getElementsByTagName("head")[0])||(a=o.body.parentNode.appendChild(o.createElement("head")));a.appendChild(e)}else if(a=="script")o.write('<script src="'+b+'" type="text/javascript"><\/script>');else a=="css"&&o.write('<link href="'+b+'" type="text/css" rel="stylesheet"></link>')};
K("google.loader.writeLoadTag",google[z].d);google[z].P=function(a){N=a};K("google.loader.rfm",google[z].P);google[z].R=function(a){for(var b in a)if(typeof b=="string"&&b&&b[s](0)==":"&&!M[b])M[b]=new T(b[A](1),a[b])};K("google.loader.rpl",google[z].R);google[z].Q=function(a){if((a=a.specs)&&a[w])for(var b=0;b<a[w];++b){var c=a[b];if(typeof c=="string")M[":"+c]=new U(c);else{c=new V(c[u],c.baseSpec,c.customSpecs);M[":"+c[u]]=c}}};K("google.loader.rm",google[z].Q);
google[z].loaded=function(a){M[":"+a.module].k(a)};K("google.loader.loaded",google[z].loaded);google[z].M=function(){var a=(new Date)[v](),b=Math.floor(Math.random()*1E7);return"qid="+(a.toString(16)+b.toString(16))};K("google.loader.createGuidArg_",google[z].M);I("google_exportSymbol",I);I("google_exportProperty",J);google[z].b={};K("google.loader.themes",google[z].b);google[z].b.B="http://www.google.com/cse/style/look/bubblegum.css";L(google[z].b,"BUBBLEGUM",google[z].b.B);google[z].b.D="http://www.google.com/cse/style/look/greensky.css";
L(google[z].b,"GREENSKY",google[z].b.D);google[z].b.C="http://www.google.com/cse/style/look/espresso.css";L(google[z].b,"ESPRESSO",google[z].b.C);google[z].b.G="http://www.google.com/cse/style/look/shiny.css";L(google[z].b,"SHINY",google[z].b.G);google[z].b.F="http://www.google.com/cse/style/look/minimalist.css";L(google[z].b,"MINIMALIST",google[z].b.F);function U(a){this.a=a;this.q=[];this.p={};this.i={};this.e={};this.l=d;this.c=-1}
U[x].g=function(a,b){var c="";if(b!=n){if(b.language!=n)c+="&hl="+j(b.language);if(b.nocss!=n)c+="&output="+j("nocss="+b.nocss);if(b.nooldnames!=n)c+="&nooldnames="+j(b.nooldnames);if(b.packages!=n)c+="&packages="+j(b.packages);if(b.callback!=g)c+="&async=2";if(b.style!=n)c+="&style="+j(b.style);if(b.other_params!=n)c+="&"+b.other_params}if(!this.l){if(google[this.a]&&google[this.a].JSHash)c+="&sig="+j(google[this.a].JSHash);var e=[];for(var f in this.p)f[s](0)==":"&&e[q](f[A](1));for(f in this.i)f[s](0)==
":"&&this.i[f]&&e[q](f[A](1));c+="&have="+j(e[B](","))}return google[z][t]+"/?file="+this.a+"&v="+a+google[z].AdditionalParams+c};U[x].z=function(a){var b=g;if(a)b=a.packages;var c=g;if(b)if(typeof b=="string")c=[a.packages];else if(b[w]){c=[];for(a=0;a<b[w];a++)typeof b[a]=="string"&&c[q](b[a][r](/^\s*|\s*$/,"")[C]())}c||(c=["default"]);b=[];for(a=0;a<c[w];a++)this.p[":"+c[a]]||b[q](c[a]);return b};
p(U[x],function(a,b){var c=this.z(b),e=b&&b.callback!=g;if(e)var f=new W(b.callback);for(var i=[],k=c[w]-1;k>=0;k--){var m=c[k];e&&f.I(m);if(this.i[":"+m]){c.splice(k,1);e&&this.e[":"+m][q](f)}else i[q](m)}if(c[w]){if(b&&b.packages)b.packages=c.sort()[B](",");for(k=0;k<i[w];k++){m=i[k];this.e[":"+m]=[];e&&this.e[":"+m][q](f)}if(!b&&N[":"+this.a]!=g&&N[":"+this.a].versions[":"+a]!=g&&!google[z].AdditionalParams&&this.l){c=N[":"+this.a];google[this.a]=google[this.a]||{};for(var R in c.properties)if(R&&
R[s](0)==":")google[this.a][R[A](1)]=c.properties[R];google[z].d("script",google[z][t]+c.path+c.js,e);c.css&&google[z].d("css",google[z][t]+c.path+c.css,e)}else if(!b||!b.autoloaded)google[z].d("script",this.g(a,b),e);if(this.l){this.l=h;this.c=(new Date)[v]();if(this.c%100!=1)this.c=-1}for(k=0;k<i[w];k++){m=i[k];this.i[":"+m]=d}}});
U[x].k=function(a){if(this.c!=-1){X("al_"+this.a,"jl."+((new Date)[v]()-this.c),d);this.c=-1}this.q=this.q.concat(a.components);google[z][this.a]||(google[z][this.a]={});google[z][this.a].packages=this.q.slice(0);for(var b=0;b<a.components[w];b++){this.p[":"+a.components[b]]=d;this.i[":"+a.components[b]]=h;var c=this.e[":"+a.components[b]];if(c){for(var e=0;e<c[w];e++)c[e].L(a.components[b]);delete this.e[":"+a.components[b]]}}X("hl",this.a)};U[x].m=function(a,b){return this.z(b)[w]==0};U[x].s=function(){return d};
function W(a){this.K=a;this.n={};this.r=0}W[x].I=function(a){this.r++;this.n[":"+a]=d};W[x].L=function(a){if(this.n[":"+a]){this.n[":"+a]=h;this.r--;this.r==0&&l[y](this.K,0)}};function V(a,b,c){this.name=a;this.J=b;this.o=c;this.w=this.h=h;this.j=[];google[z].v[this[u]]=G(this.k,this)}F(V,U);p(V[x],function(a,b){var c=b&&b.callback!=g;if(c){this.j[q](b.callback);b.callback="google.loader.callbacks."+this[u]}else this.h=d;if(!b||!b.autoloaded)google[z].d("script",this.g(a,b),c);X("el",this[u])});V[x].m=function(a,b){return b&&b.callback!=g?this.w:this.h};V[x].k=function(){this.w=d;for(var a=0;a<this.j[w];a++)l[y](this.j[a],0);this.j=[]};
var Y=function(a,b){return a.string?j(a.string)+"="+j(b):a.regex?b[r](/(^.*$)/,a.regex):""};V[x].g=function(a,b){return this.O(this.A(a),a,b)};
V[x].O=function(a,b,c){var e="";if(a.key)e+="&"+Y(a.key,google[z].ApiKey);if(a.version)e+="&"+Y(a.version,b);b=google[z].Secure&&a.ssl?a.ssl:a.uri;if(c!=g)for(var f in c)if(a.params[f])e+="&"+Y(a.params[f],c[f]);else if(f=="other_params")e+="&"+c[f];else if(f=="base_domain")b="http://"+c[f]+a.uri[A](a.uri.indexOf("/",7));google[this[u]]={};if(b.indexOf("?")==-1&&e)e="?"+e[A](1);return b+e};V[x].s=function(a){return this.A(a).deferred};
V[x].A=function(a){if(this.o)for(var b=0;b<this.o[w];++b){var c=this.o[b];if(RegExp(c.pattern).test(a))return c}return this.J};function T(a,b){this.a=a;this.f=b;this.h=h}F(T,U);p(T[x],function(a,b){this.h=d;google[z].d("script",this.g(a,b),h)});T[x].m=function(){return this.h};T[x].k=function(){};
T[x].g=function(a,b){if(!this.f.versions[":"+a]){if(this.f.aliases){var c=this.f.aliases[":"+a];if(c)a=c}if(!this.f.versions[":"+a])throw H("Module: '"+this.a+"' with version '"+a+"' not found!");}c=google[z].GoogleApisBase+"/libs/"+this.a+"/"+a+"/"+this.f.versions[":"+a][b&&b.uncompressed?"uncompressed":"compressed"];X("el",this.a);return c};T[x].s=function(){return h};var ca=h,Z=[],da=(new Date)[v](),X=function(a,b,c){if(!ca){P(l,"unload",ea);ca=d}if(c){if(!google[z].Secure&&(!google[z].Options||google[z].Options.csi===h)){a=a[C]()[r](/[^a-z0-9_.]+/g,"_");b=b[C]()[r](/[^a-z0-9_.]+/g,"_");l[y](G($,g,"http://csi.gstatic.com/csi?s=uds&v=2&action="+j(a)+"&it="+j(b)),1E4)}}else{Z[q]("r"+Z[w]+"="+j(a+(b?"|"+b:"")));l[y](ea,Z[w]>5?0:15E3)}},ea=function(){if(Z[w]){$(google[z][t]+"/stats?"+Z[B]("&")+"&nc="+(new Date)[v]()+"_"+((new Date)[v]()-da));Z.length=0}},$=function(a){var b=
new Image,c=fa++;ga[c]=b;b.onload=b.onerror=function(){delete ga[c]};b.src=a;b=g},ga={},fa=0;I("google.loader.recordStat",X);I("google.loader.createImageForLogging",$);

}) ();google.loader.rm({"specs":[{"name":"books","baseSpec":{"uri":"http://books.google.com/books/api.js","ssl":null,"key":{"string":"key"},"version":{"string":"v"},"deferred":true,"params":{"callback":{"string":"callback"},"language":{"string":"hl"}}}},"feeds",{"name":"friendconnect","baseSpec":{"uri":"http://www.google.com/friendconnect/script/friendconnect.js","ssl":null,"key":{"string":"key"},"version":{"string":"v"},"deferred":false,"params":{}}},"spreadsheets","gdata","visualization",{"name":"sharing","baseSpec":{"uri":"http://www.google.com/s2/sharing/js","ssl":null,"key":{"string":"key"},"version":{"string":"v"},"deferred":false,"params":{"language":{"string":"hl"}}}},"search",{"name":"maps","baseSpec":{"uri":"http://maps.google.com/maps?file\u003dgoogleapi","ssl":"https://maps-api-ssl.google.com/maps?file\u003dgoogleapi","key":{"string":"key"},"version":{"string":"v"},"deferred":true,"params":{"callback":{"regex":"callback\u003d$1\u0026async\u003d2"},"language":{"string":"hl"}}},"customSpecs":[{"uri":"http://maps.google.com/maps/api/js","ssl":"https://maps-api-ssl.google.com/maps/api/js","key":{"string":"key"},"version":{"string":"v"},"deferred":true,"params":{"callback":{"string":"callback"},"language":{"string":"hl"}},"pattern":"^(3|3..*)$"}]},"annotations_v2","wave","orkut",{"name":"annotations","baseSpec":{"uri":"http://www.google.com/reviews/scripts/annotations_bootstrap.js","ssl":null,"key":{"string":"key"},"version":{"string":"v"},"deferred":true,"params":{"callback":{"string":"callback"},"language":{"string":"hl"},"country":{"string":"gl"}}}},"language","earth","ads","elements"]});
google.loader.rfm({":search":{"versions":{":1":"1",":1.0":"1"},"path":"/api/search/1.0/ff53d47d54aee6066d3c78cea895cae9/","js":"default+en_GB.I.js","css":"default.css","properties":{":JSHash":"ff53d47d54aee6066d3c78cea895cae9",":NoOldNames":false,":Version":"1.0"}},":language":{"versions":{":1":"1",":1.0":"1"},"path":"/api/language/1.0/62c64af2122d2da7dcb0087852fa7396/","js":"default+en_GB.I.js","properties":{":JSHash":"62c64af2122d2da7dcb0087852fa7396",":Version":"1.0"}},":wave":{"versions":{":1":"1",":1.0":"1"},"path":"/api/wave/1.0/3b6f7573ff78da6602dda5e09c9025bf/","js":"default.I.js","properties":{":JSHash":"3b6f7573ff78da6602dda5e09c9025bf",":Version":"1.0"}},":spreadsheets":{"versions":{":0":"1",":0.3":"1"},"path":"/api/spreadsheets/0.3/8331b0bbcc74776270648505340e9200/","js":"default.I.js","properties":{":JSHash":"8331b0bbcc74776270648505340e9200",":Version":"0.3"}},":earth":{"versions":{":1":"1",":1.0":"1"},"path":"/api/earth/1.0/819ffbf1e363d238791231792a2e0a90/","js":"default.I.js","properties":{":JSHash":"819ffbf1e363d238791231792a2e0a90",":Version":"1.0"}},":annotations":{"versions":{":1":"1",":1.0":"1"},"path":"/api/annotations/1.0/11cfaf30c00ca64601d09fcac7dd8bc7/","js":"default+en.I.js","properties":{":JSHash":"11cfaf30c00ca64601d09fcac7dd8bc7",":Version":"1.0"}}});
google.loader.rpl({":scriptaculous":{"versions":{":1.8.3":{"uncompressed":"scriptaculous.js","compressed":"scriptaculous.js"},":1.8.2":{"uncompressed":"scriptaculous.js","compressed":"scriptaculous.js"},":1.8.1":{"uncompressed":"scriptaculous.js","compressed":"scriptaculous.js"}},"aliases":{":1.8":"1.8.3",":1":"1.8.3"}},":yui":{"versions":{":2.6.0":{"uncompressed":"build/yuiloader/yuiloader.js","compressed":"build/yuiloader/yuiloader-min.js"},":2.7.0":{"uncompressed":"build/yuiloader/yuiloader.js","compressed":"build/yuiloader/yuiloader-min.js"},":2.8.0r4":{"uncompressed":"build/yuiloader/yuiloader.js","compressed":"build/yuiloader/yuiloader-min.js"},":2.8.1":{"uncompressed":"build/yuiloader/yuiloader.js","compressed":"build/yuiloader/yuiloader-min.js"}},"aliases":{":2":"2.8.1",":2.7":"2.7.0",":2.6":"2.6.0",":2.8":"2.8.1",":2.8.0":"2.8.0r4"}},":swfobject":{"versions":{":2.1":{"uncompressed":"swfobject_src.js","compressed":"swfobject.js"},":2.2":{"uncompressed":"swfobject_src.js","compressed":"swfobject.js"}},"aliases":{":2":"2.2"}},":webfont":{"versions":{":1.0.2":{"uncompressed":"webfont_debug.js","compressed":"webfont.js"},":1.0.1":{"uncompressed":"webfont_debug.js","compressed":"webfont.js"},":1.0.0":{"uncompressed":"webfont_debug.js","compressed":"webfont.js"},":1.0.6":{"uncompressed":"webfont_debug.js","compressed":"webfont.js"},":1.0.5":{"uncompressed":"webfont_debug.js","compressed":"webfont.js"},":1.0.4":{"uncompressed":"webfont_debug.js","compressed":"webfont.js"},":1.0.3":{"uncompressed":"webfont_debug.js","compressed":"webfont.js"}},"aliases":{":1":"1.0.6",":1.0":"1.0.6"}},":ext-core":{"versions":{":3.1.0":{"uncompressed":"ext-core-debug.js","compressed":"ext-core.js"},":3.0.0":{"uncompressed":"ext-core-debug.js","compressed":"ext-core.js"}},"aliases":{":3":"3.1.0",":3.0":"3.0.0",":3.1":"3.1.0"}},":mootools":{"versions":{":1.2.3":{"uncompressed":"mootools.js","compressed":"mootools-yui-compressed.js"},":1.1.1":{"uncompressed":"mootools.js","compressed":"mootools-yui-compressed.js"},":1.2.4":{"uncompressed":"mootools.js","compressed":"mootools-yui-compressed.js"},":1.2.1":{"uncompressed":"mootools.js","compressed":"mootools-yui-compressed.js"},":1.2.2":{"uncompressed":"mootools.js","compressed":"mootools-yui-compressed.js"},":1.1.2":{"uncompressed":"mootools.js","compressed":"mootools-yui-compressed.js"}},"aliases":{":1":"1.1.2",":1.11":"1.1.1",":1.2":"1.2.4",":1.1":"1.1.2"}},":jqueryui":{"versions":{":1.7.2":{"uncompressed":"jquery-ui.js","compressed":"jquery-ui.min.js"},":1.7.3":{"uncompressed":"jquery-ui.js","compressed":"jquery-ui.min.js"},":1.6.0":{"uncompressed":"jquery-ui.js","compressed":"jquery-ui.min.js"},":1.7.0":{"uncompressed":"jquery-ui.js","compressed":"jquery-ui.min.js"},":1.7.1":{"uncompressed":"jquery-ui.js","compressed":"jquery-ui.min.js"},":1.5.3":{"uncompressed":"jquery-ui.js","compressed":"jquery-ui.min.js"},":1.8.0":{"uncompressed":"jquery-ui.js","compressed":"jquery-ui.min.js"},":1.5.2":{"uncompressed":"jquery-ui.js","compressed":"jquery-ui.min.js"},":1.8.2":{"uncompressed":"jquery-ui.js","compressed":"jquery-ui.min.js"},":1.8.1":{"uncompressed":"jquery-ui.js","compressed":"jquery-ui.min.js"}},"aliases":{":1.8":"1.8.2",":1.7":"1.7.3",":1.6":"1.6.0",":1":"1.8.2",":1.5":"1.5.3"}},":chrome-frame":{"versions":{":1.0.2":{"uncompressed":"CFInstall.js","compressed":"CFInstall.min.js"},":1.0.1":{"uncompressed":"CFInstall.js","compressed":"CFInstall.min.js"},":1.0.0":{"uncompressed":"CFInstall.js","compressed":"CFInstall.min.js"}},"aliases":{":1":"1.0.2",":1.0":"1.0.2"}},":prototype":{"versions":{":1.6.0.2":{"uncompressed":"prototype.js","compressed":"prototype.js"},":1.6.1.0":{"uncompressed":"prototype.js","compressed":"prototype.js"},":1.6.0.3":{"uncompressed":"prototype.js","compressed":"prototype.js"}},"aliases":{":1.6.1":"1.6.1.0",":1":"1.6.1.0",":1.6":"1.6.1.0",":1.6.0":"1.6.0.3"}},":jquery":{"versions":{":1.2.3":{"uncompressed":"jquery.js","compressed":"jquery.min.js"},":1.3.1":{"uncompressed":"jquery.js","compressed":"jquery.min.js"},":1.3.0":{"uncompressed":"jquery.js","compressed":"jquery.min.js"},":1.3.2":{"uncompressed":"jquery.js","compressed":"jquery.min.js"},":1.2.6":{"uncompressed":"jquery.js","compressed":"jquery.min.js"},":1.4.0":{"uncompressed":"jquery.js","compressed":"jquery.min.js"},":1.4.1":{"uncompressed":"jquery.js","compressed":"jquery.min.js"},":1.4.2":{"uncompressed":"jquery.js","compressed":"jquery.min.js"}},"aliases":{":1":"1.4.2",":1.4":"1.4.2",":1.3":"1.3.2",":1.2":"1.2.6"}},":dojo":{"versions":{":1.2.3":{"uncompressed":"dojo/dojo.xd.js.uncompressed.js","compressed":"dojo/dojo.xd.js"},":1.3.1":{"uncompressed":"dojo/dojo.xd.js.uncompressed.js","compressed":"dojo/dojo.xd.js"},":1.1.1":{"uncompressed":"dojo/dojo.xd.js.uncompressed.js","compressed":"dojo/dojo.xd.js"},":1.3.0":{"uncompressed":"dojo/dojo.xd.js.uncompressed.js","compressed":"dojo/dojo.xd.js"},":1.3.2":{"uncompressed":"dojo/dojo.xd.js.uncompressed.js","compressed":"dojo/dojo.xd.js"},":1.4.3":{"uncompressed":"dojo/dojo.xd.js.uncompressed.js","compressed":"dojo/dojo.xd.js"},":1.5.0":{"uncompressed":"dojo/dojo.xd.js.uncompressed.js","compressed":"dojo/dojo.xd.js"},":1.2.0":{"uncompressed":"dojo/dojo.xd.js.uncompressed.js","compressed":"dojo/dojo.xd.js"},":1.4.0":{"uncompressed":"dojo/dojo.xd.js.uncompressed.js","compressed":"dojo/dojo.xd.js"},":1.4.1":{"uncompressed":"dojo/dojo.xd.js.uncompressed.js","compressed":"dojo/dojo.xd.js"}},"aliases":{":1":"1.5.0",":1.5":"1.5.0",":1.4":"1.4.3",":1.3":"1.3.2",":1.2":"1.2.3",":1.1":"1.1.1"}}});
}
