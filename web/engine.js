/* Portable game rules. No DOM, network, dependencies, eval, or Python runtime. */
(function(root) {
  'use strict';
  function createEngine(D) {
    const has=(obj,key)=>Object.prototype.hasOwnProperty.call(obj,key);
    const I=D.items, slots=D.slots, clamp=(v,a=0,b=100)=>Math.max(a,Math.min(b,v));
    const copy=v=>JSON.parse(JSON.stringify(v));
    const mod=v=>Math.floor((v-10)/2);
    function rand(r) { // Serializable Mulberry32 stream; browser seeds are independent of Python's RNG.
      r.rng=(r.rng+0x6D2B79F5)>>>0;
      let t=r.rng;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);
      return ((t^(t>>>14))>>>0)/4294967296;
    }
    const roll=(r,n)=>1+Math.floor(rand(r)*n);
    const pick=(r,a)=>a[Math.floor(rand(r)*a.length)];
    function sample(r,a,n) { const x=[...a];for(let j=x.length-1;j>0;j--){const k=Math.floor(rand(r)*(j+1));[x[j],x[k]]=[x[k],x[j]];}return x.slice(0,n); }
    function weighted(r,a) {const weights={Gewöhnlich:8,Selten:4,Episch:2,Legendär:1};let t=rand(r)*a.reduce((s,k)=>s+weights[I[k].rarity],0);return a.find(k=>(t-=weights[I[k].rarity])<0)||a[a.length-1];}
    function note(r,text){r.log.push(text);r.log=r.log.slice(-120);}
    function add(r,key){if(!I[key])return null;const o={uid:++r.serial,key,age:0,cold_chain_ok:true};if(I[key].durability)o.durability=I[key].durability;r.inventory.push(o);return o.uid;}
    function attrRoll(r) {const rng={rng:(r.seed^Math.imul(r.rerolls+1,0x9E3779B9))>>>0};r.attributes={};r.attribute_dice={};for(const k of Object.keys(D.attributes)){const ds=Array.from({length:4},()=>roll(rng,6));r.attribute_dice[k]=ds;r.attributes[k]=[...ds].sort((a,b)=>b-a).slice(0,3).reduce((a,b)=>a+b,0);}}
    function newRun(seed=42) {
      const r={seed:Number(seed)>>>0,rng:Number(seed)>>>0,phase:'creation',day:1,step:0,turn:0,hp:100,energy:85,water:85,fullness:20,nausea:0,xp:0,level:1,
        rescued:0,shared:0,fairteiler_shared:0,wins:0,inventory:[],equipped:{},serial:0,log:['Die fünftägige Rettungstour beginnt.'],options:[],enemy:null,loot:[],combat:[],
        rerolls:0,character_name:'Alex',background:null,last_check:null,hygiene:100,gas:0,urgency:0,salt_load:0,digestion:[],effects:{},last_retch:-10,
        trust:50,business_pickups:0,responsible_choices:0,violations:[],claimed:[],supported_days:[],standing:{},hygiene_log:[],distribution_log:[],basket:null};
      for(const key of ['baguette','apron','tote','water','tea','bandage','banana','bread']){const id=add(r,key);if(slots[I[key].kind])r.equipped[I[key].kind]=id;}
      for(const key of ['cotton_gloves','cloth_mask','soap'])add(r,key);
      attrRoll(r);makeOptions(r);return r;
    }
    const object=(r,uid)=>r.inventory.find(o=>o.uid===Number(uid));
    const worn=(r,o)=>Object.values(r.equipped).includes(o.uid);
    function bonus(r,key){let n=r.inventory.filter(o=>worn(r,o)&&(o.durability??1)>0).reduce((s,o)=>s+(I[o.key][key]||0),0);const e=r.effects[key];return n+(e&&r.turn<e.until?e.power:0);}
    function stats(r){return {attack:7+2*(r.level-1)+bonus(r,'attack'),defense:bonus(r,'defense'),capacity:18+mod(r.attributes.strength||10)*2+bonus(r,'capacity'),cooling:bonus(r,'cooling')};}
    const weight=r=>r.inventory.reduce((s,o)=>s+I[o.key].weight,0);
    const freshness=o=>Math.max(0,(I[o.key].shelf??999)-o.age)<1e-9?0:Math.max(0,(I[o.key].shelf??999)-o.age);
    function chance(b,dc){let n=0;for(let f=1;f<=20;f++)if(f===20||(f!==1&&f+b>=dc))n++;return n*5;}
    function preview(r,attribute,dc){let tool=0;const o=object(r,r.equipped.weapon);if(o&&(o.durability??1)>0){const b=D.toolBonuses[o.key];if(b&&b[0]===attribute)tool=b[1];}
      const p={attribute,dc,base:mod(r.attributes[attribute]||10),tool,equipment:bonus(r,attribute),fatigue:r.energy<25?-2:0,stomach:r.nausea>=50?-2:0,community:attribute==='presence'?(r.trust>=70?1:r.trust<25?-1:0):0};
      p.bonus=p.base+p.tool+p.equipment+p.fatigue+p.stomach+p.community;p.chance=chance(p.bonus,dc);return p;}
    function spec(r,action,option=r.encounter||{}){const danger=option.danger||1;if(action==='attack')return preview(r,option.kind==='business'?D.venueStats[option.venue]:'dexterity',10+danger-(option.kind==='business'&&(r.standing[option.venue]||0)>=2?1:0));
      if(action==='heavy')return preview(r,'strength',13+danger);if(action==='defend')return preview(r,'dexterity',12);if(action==='flee')return preview(r,'presence',14);
      if(action==='bin'){const b=D.bins[r.bin_key];return preview(r,b.stat,b.dc);}return preview(r,r.event==='rain'?'dexterity':'strength',14);}
    function resolve(r,p){const f=roll(r,20);r.last_check={...p,roll:f,total:f+p.bonus,success:f===20||(f!==1&&f+p.bonus>=p.dc)};note(r,summary(r.last_check));return r.last_check.success;}
    const signed=n=>n>=0?'+'+n:String(n);
    function summary(c){return `${D.attributes[c.attribute]}: W20 ${c.roll} ${signed(c.bonus)} = ${c.total} gegen SG ${c.dc} → ${c.success?'Erfolg':'Misserfolg'}${c.roll===1?' (natürliche 1)':c.roll===20?' (natürliche 20)':''}`;}
    function end(r){r.hp=Math.min(100+(r.level-1)*8,r.hp);if(r.hp<=0){r.hp=0;r.phase='dead';note(r,'Für heute reicht die Kraft nicht mehr. Das Betriebsteam organisiert Ersatz.');}}
    function tick(r){const s=stats(r),save=bonus(r,'energy_save'),dig=bonus(r,'digestion');r.turn++;r.energy=Math.max(0,r.energy-Math.max(1,3-save));r.water=Math.max(0,r.water-3);r.fullness=Math.max(0,r.fullness-5);r.nausea=Math.max(0,r.nausea-2);
      for(const o of r.inventory){if(I[o.key].cold&&!s.cooling)o.cold_chain_ok=false;o.age+=I[o.key].cold&&s.cooling?1/3:1;}
      if(r.salt_load>=10)r.water=Math.max(0,r.water-1);r.salt_load=Math.max(0,r.salt_load-1);
      if(r.digestion.length){const m=r.digestion[0],a=Math.min(m.energy,Math.max(1,4+dig-(m.fat>=5?1:0)));m.energy-=a;r.energy=clamp(r.energy+a);r.urgency=clamp(r.urgency+3);if(m.energy<=0)r.digestion.shift();}
      r.gas=Math.max(0,r.gas-2);if(r.gas>=60)r.nausea=clamp(r.nausea+2);if(r.urgency>=80)r.energy=Math.max(0,r.energy-2);
      if(r.nausea>=90&&r.fullness>0&&r.turn-r.last_retch>=4){r.fullness=Math.max(0,r.fullness-30);r.water=Math.max(0,r.water-12);r.nausea=Math.max(0,r.nausea-20);r.last_retch=r.turn;note(r,'Der Spielmagen rebelliert: −30 Füllung, −12 Wasser, −20 Übelkeit.');}
      for(const o of r.inventory)if(worn(r,o)&&o.durability>0){o.durability--;if(!o.durability)note(r,I[o.key].name+' ist verschlissen.');}
      for(const k of Object.keys(r.effects))if(r.effects[k].until<=r.turn)delete r.effects[k];
      if(!r.energy||!r.water){r.hp-=6;note(r,'Erschöpfung oder Durst: −6 Kraft.');}if(r.nausea>=70){r.hp-=5;note(r,'Magenkrämpfe: −5 Kraft.');}if(weight(r)>s.capacity)r.energy=Math.max(0,r.energy-5);end(r);
    }
    const reserved=(r,uid)=>!!r.basket&&r.basket.uids.includes(Number(uid));
    function equip(r,uid){const o=object(r,uid);if(r.phase!=='map'||!o||!slots[I[o.key].kind])return false;r.equipped[I[o.key].kind]=o.uid;note(r,I[o.key].name+' angelegt.');return true;}
    function consume(r,uid){const o=object(r,uid);if(!['map','combat'].includes(r.phase)||!o||reserved(r,o.uid))return false;const d=I[o.key];if(!['food','consumable'].includes(d.kind))return false;let e=d.energy||0;
      if(d.kind==='food'){let risk=(d.risk||0)+(freshness(o)===0?50:0)+(d.cold&&!o.cold_chain_ok?20:0)+Math.max(0,Math.floor((60-r.hygiene)/3));r.nausea=clamp(r.nausea+risk+Math.max(0,r.fullness+d.fullness-85));r.fullness=clamp(r.fullness+d.fullness);r.gas=clamp(r.gas+(d.fiber||0)*3);r.salt_load=clamp(r.salt_load+(d.salt||0),0,50);const now=Math.floor(e/3);if(e>now)r.digestion.push({name:d.name,energy:e-now,fat:d.fat||0});e=now;
      }else{r.nausea=clamp(r.nausea+(d.nausea||0));r.hygiene=clamp(r.hygiene+(d.hygiene||0));r.gas=clamp(r.gas+(d.gas||0));if(d.effect)r.effects[d.effect]={power:d.power,until:r.turn+d.turns+1};
        if(d.repair)for(const target of r.inventory){const t=I[target.key];if(worn(r,target)&&t.durability&&(!d.repair_slot||d.repair_slot===t.kind))target.durability=Math.min(t.durability,(target.durability||0)+d.repair);}}
      r.hp+=d.heal||0;r.energy=clamp(r.energy+e);r.water=clamp(r.water+(d.water||0));r.inventory=r.inventory.filter(x=>x.uid!==o.uid);note(r,d.name+' verbraucht.');const defense=stats(r).defense;tick(r);if(r.phase==='combat')enemyTurn(r,0,defense);end(r);return true;
    }
    function makeOptions(r){if(r.day===5&&r.step===3){r.options=[{kind:'business',venue:4,danger:3}];return;}r.options=sample(r,D.businesses.map((_,i)=>i),2).map(venue=>({kind:'business',venue,danger:roll(r,3)}));r.options.push({kind:pick(r,['camp','event','arena','bins']),danger:1});}
    function advance(r){r.step++;if(r.step===4){if(r.day===5){r.phase='victory';note(r,'Freitag: Die letzte Abholung ist unterwegs. Sam stellt die Teekanne auf.');return;}r.day++;r.step=0;r.energy=clamp(r.energy+25);r.water=clamp(r.water+25);r.hp+=15;}r.phase='map';r.enemy=null;r.loot=[];makeOptions(r);end(r);}
    function visit(r,index){if(r.phase!=='map'||!r.options[index])return false;const o=r.options[index];tick(r);if(r.phase==='dead')return true;
      if(o.kind==='business'){r.pending_route=index;r.phase='briefing';r.briefing_feedback=null;r.last_check=null;}
      else if(o.kind==='camp'){r.phase='camp';note(r,'Du erreichst den Bezirkstreff.');}
      else if(o.kind==='event'){r.phase='event';r.event=pick(r,Object.keys(D.events));}
      else if(o.kind==='bins')beginBin(r,pick(r,Object.keys(D.bins)));else beginEncounter(r,o);return true;}
    function briefing(r){const o=r.options[r.pending_route];return D.briefings[(o.venue+r.day+r.step)%D.briefings.length];}
    function prepare(r,p){if(r.phase!=='briefing')return false;const b=briefing(r);if(!p.papers||!p.notes||!p.containers||!p.hands){r.briefing_feedback='Prüfe erst Ausweis, Absprachen, Behälter und Handhygiene.';return true;}if(Number(p.response)!==b.correct){r.briefing_feedback=b.why+' Du kannst die Antwort korrigieren; keine Regelmeldung.';return true;}note(r,b.why);r.briefing_feedback=null;r.last_check=null;beginEncounter(r,r.options[r.pending_route]);return true;}
    function beginEncounter(r,o){const boss=r.day===5&&r.step===3,story=boss?D.final:o.kind==='business'?D.encounters[o.venue]:null;const hp=26+r.day*9+o.danger*4+(boss?35:0);r.phase='combat';r.encounter=copy(o);r.enemy={name:story?story.name:pick(r,['Sam · Trainingspartnerin (NPC)','Hannes · Trainingspartner (NPC)','Deniz · Trainingspartner (NPC)']),hp,max_hp:hp,attack:7+r.day*2+o.danger,intent:'attack',boss,narrative:story};r.combat=[story?story.opening:'Der freiwillige Abhol-Parcours beginnt.'];}
    function enemyTurn(r,block=0,defense=stats(r).defense){const e=r.enemy;if(e.intent==='recover'){r.combat.push(e.narrative?e.narrative.recover:'Dein Trainingspartner holt Luft.');e.intent='attack';return;}const hit=Math.max(1,e.attack+roll(r,5)-3-defense-block);r.hp-=hit;r.combat.push((e.narrative?e.narrative.hit:'Dein Trainingspartner legt vor.')+` −${hit} Kraft.`);e.intent=pick(r,['attack','attack','recover']);end(r);}
    function combat(r,action){if(r.phase!=='combat'||!['attack','heavy','defend','flee'].includes(action)||action==='heavy'&&r.energy<15||action==='flee'&&r.enemy.boss)return false;const p=spec(r,action),s=stats(r);tick(r);if(r.phase==='dead')return true;const ok=resolve(r,p),e=r.enemy;
      if(action==='flee'){if(ok){note(r,'Ersatz übernimmt die Abholung; keine Lebensmittel mitgenommen.');advance(r);return true;}r.combat.push('Du erreichst noch keinen Ersatz.');}
      else if(action!=='defend'){let hit=s.attack+roll(r,5)-1;if(action==='heavy'){r.energy-=12;hit=ok?Math.floor(hit*1.8):0;}else if(!ok)hit=Math.max(1,Math.floor(hit/2));if(r.nausea>=50&&hit)hit=Math.max(1,hit-5);e.hp=Math.max(0,e.hp-hit);r.combat.push(`Dein Fortschritt: ${hit}.`);}
      if(!e.hp){reward(r);return true;}enemyTurn(r,action==='defend'?(ok?9:3):0,s.defense);r.combat=r.combat.slice(-8);return true;}
    function reward(r){if(r.encounter.kind==='business'){r.business_pickups++;r.standing[r.encounter.venue]=(r.standing[r.encounter.venue]||0)+1;r.trust=clamp(r.trust+2);}r.wins++;r.xp+=12;if(r.xp>=r.level*20){r.level++;r.hp+=18;note(r,`Level ${r.level}! +18 Kraft.`);}const foods=r.encounter.kind==='business'?D.foods[r.encounter.venue]:['snack','water'];const gear=Object.keys(I).filter(k=>slots[I[k].kind]);r.loot=[pick(r,foods),pick(r,foods),weighted(r,gear),pick(r,Object.keys(I).filter(k=>I[k].kind==='consumable')),'water'];r.phase='loot';note(r,r.enemy.narrative?r.enemy.narrative.done:'Trainingsrunde gewonnen. Material liegt bereit.');}
    function take(r,index,bin=false){const list=bin?r.bin_loot:r.loot;if(r.phase!==(bin?'bin_loot':'loot')||!list[index])return false;const k=list[index];if(weight(r)+I[k].weight>stats(r).capacity)return false;add(r,k);list.splice(index,1);if(!bin&&r.encounter.kind==='business'&&I[k].kind==='food')r.rescued++;note(r,I[k].name+' eingepackt.');return true;}
    function finishLoot(r){if(r.phase!=='loot')return false;if(r.encounter.kind==='business'&&!r.enemy.boss&&r.business_pickups%2===0){const v=r.encounter.venue;r.incident=[2,3].includes(v)?'cold':[1,5,7].includes(v)?'sorting':'handoff';r.phase='incident';r.last_check=null;}else advance(r);return true;}
    function incident(r,choice){if(r.phase!=='incident'||!['good','bad','ask'].includes(choice))return false;const d=D.incidents[r.incident];if(choice==='bad'){r.violations.push({title:d.title,rule:d.rule,day:r.day,resolved:false});r.trust=clamp(r.trust-15);r.energy=clamp(r.energy+10);note(r,d.title+': bewusste Abkürzung. −15 Zusammenhalt, +10 Energie. Robin sucht das persönliche Gespräch; keine ungeprüfte Weitergabe.');}else{const cost=choice==='ask'?(resolve(r,preview(r,'presence',13))?2:8):5;r.energy=Math.max(0,r.energy-cost);r.responsible_choices++;r.trust=clamp(r.trust+5);note(r,d.title+`: verantwortungsvoll geklärt. −${cost} Energie, +5 Zusammenhalt.`);}advance(r);return true;}
    function community(r,action,key){if(r.phase!=='map')return false;if(action==='support'){if(r.trust<40||r.supported_days.includes(r.day))return false;r.supported_days.push(r.day);r.hp+=12;r.water=clamp(r.water+30);r.energy=clamp(r.energy+20);tick(r);note(r,'Robin organisiert mit dem Betriebsteam eine Vertretung.');}
      else if(action==='repairIncident'){const v=r.violations[key];if(!v||v.resolved||r.energy<11)return false;v.resolved=true;r.energy-=8;r.trust=clamp(r.trust+7);tick(r);note(r,v.title+': persönliches Gespräch geführt. +7 Zusammenhalt.');}
      else if(action==='claim'){const q=has(D.requests,key)?D.requests[key]:null;if(!q||r.claimed.includes(key)||r[q.counter]<q.target||weight(r)+I[q.reward].weight>stats(r).capacity)return false;r.claimed.push(key);add(r,q.reward);r.trust=clamp(r.trust+5);note(r,q.title+': Material bereitgestellt.');}else return false;return true;}
    function event(r,cautious){if(r.phase!=='event')return false;const d=D.events[r.event];if(cautious){r.energy=clamp(r.energy+8);note(r,'Kurze Pause: +8 Energie.');}else if(resolve(r,spec(r,'event'))){const k=pick(r,['cooler','vest','rolling','medkit','cargo']);if(weight(r)+I[k].weight<=stats(r).capacity){add(r,k);note(r,d.success+' '+I[k].name);}else note(r,'Für den Materialfund ist kein Platz.');}else{r.hp-=15;r.nausea=clamp(r.nausea+10);note(r,d.failure+' −15 Kraft, +10 Übelkeit.');}end(r);if(r.phase!=='dead')advance(r);return true;}
    const selected=(r,ids)=>{if(!Array.isArray(ids)||!ids.length||new Set(ids).size!==ids.length)return [];const list=r.inventory.filter(o=>ids.includes(o.uid));return list.length===ids.length?list:[];};
    function eligible(r,o,channel,refrigerated=true,basket=false){const d=I[o.key];if(d.kind!=='food')return [false,'Kein Lebensmittel.'];if(reserved(r,o.uid)&&!basket)return [false,'Für den Essenskorb reserviert.'];if(freshness(o)<=0)return [false,'Keine Genießbarkeit im Spiel.'];if(d.cold&&!o.cold_chain_ok)return [false,'Kühlkette im Spiel länger unterbrochen.'];if(channel==='fairteiler'){if(['salad','soup','cake'].includes(o.key)||d.personal_only)return [false,'Zubereitete warme/kühlbedürftige Speise: nur persönliche Übergabe.'];if(d.cold&&(!refrigerated||!r.hygiene_log.some(e=>e.day===r.day)))return [false,'Kein kontrollierter Kühlschrank verfügbar.'];}return [true,'Geeignet im vereinfachten Spielmodell; vor Übergabe prüfen.'];}
    function handover(r,objects,channel){const names=objects.map(o=>I[o.key].name),ids=new Set(objects.map(o=>o.uid));r.inventory=r.inventory.filter(o=>!ids.has(o.uid));r.shared+=objects.length;if(channel==='fairteiler')r.fairteiler_shared+=objects.length;r.hp+=5*objects.length;r.distribution_log.push({day:r.day,channel,names});note(r,`${D.channels[channel]}: ${names.join(', ')}. Kostenlos und bedingungslos; +5 Kraft je Posten als Spielbonus.`);}
    function share(r,p){if(r.phase!=='map'||!p.checked)return false;const channel=p.channel;if(!['personal','fairteiler','basket'].includes(channel)||channel==='personal'&&!p.conversation)return false;const list=selected(r,p.uids);if(!list.length||!list.every(o=>eligible(r,o,channel==='basket'?'personal':channel)[0]))return false;if(channel==='basket'){if(r.basket)return false;r.basket={uids:p.uids,ready_turn:r.turn+2};note(r,'Fiktiver Essenskorb angelegt. Ware bleibt reserviert; nichts online veröffentlicht.');}else handover(r,list,channel);tick(r);return true;}
    function basket(r,action,p={}){if(r.phase!=='map'||!r.basket)return false;if(action==='cancel'){r.basket=null;note(r,'Essenskorb zurückgenommen.');return true;}if(action==='wait'){if(r.turn>=r.basket.ready_turn)return false;tick(r);return true;}if(action==='deliver'){const list=selected(r,r.basket.uids);if(r.turn<r.basket.ready_turn||!p.checked||!p.conversation||!list.length||!list.every(o=>eligible(r,o,'personal',true,true)[0]))return false;handover(r,list,'basket');r.basket=null;tick(r);return true;}return false;}
    function maintain(r){if(r.phase!=='map'||r.hygiene_log.some(e=>e.day===r.day))return false;r.hygiene_log.push({day:r.day,temperature:5,cleaned:true});note(r,'Fairteiler kontrolliert: fiktive Messung 5 °C; Hygieneplan geführt.');tick(r);return true;}
    function camp(r,action){if(r.phase!=='camp'||!['rest','share'].includes(action))return false;if(action==='rest'){r.hp+=30;r.energy=clamp(r.energy+35);r.water=clamp(r.water+35);r.nausea=Math.max(0,r.nausea-35);note(r,'Pause: +30 Kraft, +35 Energie/Wasser, −35 Übelkeit.');}else{const list=r.inventory.filter(o=>eligible(r,o,'fairteiler',false)[0]);if(list.length)handover(r,list,'fairteiler');else note(r,'Keine geeigneten unreservierten Lebensmittel fürs ungekühlte Regal.');}advance(r);return true;}
    function beginBin(r,key){r.bin_key=key;r.phase='bins';r.last_check=null;r.bin_loot=[];r.bin_result='';}
    function chooseBin(r,key){if(r.phase!=='map'||!has(D.bins,key)||r.day===5&&r.step===3)return false;tick(r);if(r.phase!=='dead')beginBin(r,key);return true;}
    function binAction(r,action,index){if(action==='leave'){if(!['bins','bin_loot'].includes(r.phase))return false;r.bin_loot=[];advance(r);return true;}if(action==='take')return take(r,index,true);if(action!=='resolve'||r.phase!=='bins')return false;const d=D.bins[r.bin_key],p=spec(r,'bin'),pro={};for(const k of ['handling','dust_guard','odor_guard','grip'])pro[k]=bonus(r,k);tick(r);if(r.phase==='dead')return true;const ok=resolve(r,p);const dirt=Math.max(0,d.dirt-pro.handling),odor=Math.max(0,d.odor-pro.odor_guard),strain=Math.max(0,d.dust-pro.dust_guard)+(ok?0:Math.max(2,12-pro.grip));r.hygiene=Math.max(0,r.hygiene-dirt);r.nausea=clamp(r.nausea+odor);r.hp-=strain;r.bin_loot=ok?sample(r,d.loot,2):[];r.bin_result=`${ok?'Sortierrunde gelungen':'Suche abgebrochen'}: −${dirt} Hygiene, +${odor} Übelkeit, −${strain} Kraft.`;note(r,r.bin_result);r.phase='bin_loot';end(r);return true;}
    function bodyAction(r,action){if(r.phase!=='map')return false;if(action==='wash'){if(r.water<8||r.hygiene===100)return false;r.water-=5;r.hygiene=100;note(r,'Hände gewaschen; −5 Wasser plus eine Runde.');}else if(action==='restroom'){if(!r.urgency&&!r.gas&&!r.nausea)return false;r.urgency=0;r.gas=Math.max(0,r.gas-25);r.nausea=Math.max(0,r.nausea-10);note(r,'Toilettenpause eingelegt.');}else return false;tick(r);return true;}
    function act(r,action,p={}){switch(action){case 'reroll':if(r.phase!=='creation'||r.rerolls>=2)return false;r.rerolls++;attrRoll(r);return true;
      case 'confirm':if(r.phase!=='creation'||!has(D.backgrounds,p.background))return false;r.character_name=String(p.name||'Alex').trim().slice(0,30)||'Alex';r.background=p.background;r.attributes[D.backgrounds[p.background][0]]+=2;r.phase='map';note(r,r.character_name+' übernimmt die Runde.');return true;
      case 'visit':return visit(r,Number(p.index));case 'prepare':return prepare(r,p);case 'combat':return combat(r,p.move);case 'take':return take(r,Number(p.index));case 'finishLoot':return finishLoot(r);case 'incident':if(p.choice==='bad'&&!p.ack)return false;return incident(r,p.choice);
      case 'equip':return equip(r,p.uid);case 'unequip':if(r.phase!=='map'||!r.equipped[p.slot])return false;delete r.equipped[p.slot];return true;
      case 'consume':return consume(r,p.uid);case 'drop':if(r.phase!=='map'||reserved(r,p.uid)||!object(r,p.uid)||worn(r,object(r,p.uid)))return false;r.inventory=r.inventory.filter(o=>o.uid!==Number(p.uid));return true;
      case 'camp':return camp(r,p.choice);case 'event':return event(r,p.cautious);case 'support':case 'repairIncident':case 'claim':return community(r,action,p.key);
      case 'maintain':return maintain(r);case 'share':return share(r,p);case 'basket':return basket(r,p.move,p);case 'chooseBin':return chooseBin(r,p.key);case 'bin':return binAction(r,p.move,Number(p.index));case 'body':return bodyAction(r,p.move);default:return false;}}
    function newDuel(a,b,weapon='baguette'){if(!I[weapon]||I[weapon].kind!=='weapon')weapon='baguette';return {players:[a,b].map((name,i)=>({name:String(name||'Spieler '+(i+1)).slice(0,30),hp:100,weapon,stamina:40,potions:2,guard:false})),turn:0,winner:null,log:['Spieler 1 beginnt.']};}
    function duel(d,action){if(d.winner!==null||!['attack','heavy','defend','heal'].includes(action))return false;const a=d.players[d.turn],b=d.players[1-d.turn];if(action==='heavy'&&a.stamina<12||action==='heal'&&!a.potions)return false;a.guard=false;let message;
      if(action==='defend'){a.guard=true;a.stamina=clamp(a.stamina+10,0,40);message=a.name+' sichert ab und regeneriert 10 Ausdauer.';}else if(action==='heal'){a.potions--;a.hp=clamp(a.hp+24);message=a.name+' nutzt eine Versorgungspause.';}else{let hit=8+I[a.weapon].attack;if(action==='heavy'){a.stamina-=12;hit=Math.floor(hit*1.7);}else a.stamina=clamp(a.stamina+3,0,40);hit=Math.max(1,hit-(b.guard?12:0));b.hp=Math.max(0,b.hp-hit);message=`${a.name} legt vor. ${b.name} verliert ${hit} Kondition.`;}
      d.log=[...d.log,message].slice(-12);if(!b.hp)d.winner=d.turn;else d.turn=1-d.turn;return true;}
    function newLearner(){return {stage:'intro',name:'Alex',quiz:0,pickup:0,answered:false,feedback:null,mistakes:0,log:[]};}
    function learn(l,action,p={}){if(action==='start'&&l.stage==='intro'){l.name=String(p.name||'Alex').trim().slice(0,30)||'Alex';l.stage='quiz';return true;}
      if(action==='answer'&&['quiz','pickup'].includes(l.stage)&&!l.answered){const q=l.stage==='quiz'?D.learning.QUIZ[l.quiz]:D.learning.PICKUPS[l.pickup],correct=l.stage==='quiz'?q[3]:q.correct;l.answered=Number(p.index)===correct;l.feedback=(l.answered?'Gut entschieden. ':'Noch einmal überlegen. ')+(l.stage==='quiz'?q[4]:q.why);if(!l.answered)l.mistakes++;return true;}
      if(action==='next'&&l.answered){if(l.stage==='quiz'){l.quiz++;if(l.quiz===D.learning.QUIZ.length)l.stage='agreement';}else if(l.stage==='pickup'){l.log.push('Tour '+(l.pickup+1)+': '+D.learning.PICKUPS[l.pickup].title);l.pickup++;if(l.pickup===D.learning.PICKUPS.length)l.stage='verification';}l.answered=false;l.feedback=null;return true;}
      if(action==='agree'&&l.stage==='agreement'&&p.ack){l.stage='pickup';return true;}if(action==='finish'&&l.stage==='verification'){l.stage='finish';return true;}return false;}
    // Validate imported saves before they can affect the live session. No executable data.
    function validate(s){const bad=()=>{throw new Error('Unbekannter oder beschädigter Spielstand.');};
      const plain=v=>v&&typeof v==='object'&&!Array.isArray(v);
      if(!plain(s)||s.version!==1||!plain(s.run)||!plain(s.learn)||!plain(s.prefs))bad();
      if(typeof s.prefs.sound!=='boolean'||typeof s.prefs.motion!=='boolean'||!['route','bag','sharing','district','bins','arena','codex','learn'].includes(s.prefs.tab))bad();const r=s.run;
      if(!['creation','map','briefing','combat','loot','camp','event','incident','bins','bin_loot','dead','victory'].includes(r.phase))bad();
      const numeric=['seed','rng','day','step','turn','hp','energy','water','fullness','nausea','xp','level','rescued','shared','fairteiler_shared','wins','serial','rerolls','hygiene','gas','urgency','salt_load','last_retch','trust','business_pickups','responsible_choices'];
      if(numeric.some(k=>!Number.isFinite(r[k]))||r.day<1||r.day>5||r.step<0||r.step>4||r.turn<0||r.level<1||r.rerolls<0||r.rerolls>2)bad();
      for(const k of ['energy','water','fullness','nausea','hygiene','gas','urgency','trust'])if(r[k]<0||r[k]>100)bad();
      for(const k of ['inventory','log','options','loot','digestion','violations','claimed','supported_days','hygiene_log','distribution_log'])if(!Array.isArray(r[k])||r[k].length>10000)bad();
      if(!plain(r.attributes)||Object.keys(D.attributes).some(k=>!Number.isInteger(r.attributes[k])||r.attributes[k]<3||r.attributes[k]>20)||!plain(r.equipped)||!plain(r.effects)||!plain(r.standing))bad();
      const ids=new Set();for(const o of r.inventory){if(!o||typeof o.key!=='string'||!has(I,o.key)||!Number.isSafeInteger(o.uid)||o.uid<=0||ids.has(o.uid)||!Number.isFinite(o.age)||o.age<0||typeof o.cold_chain_ok!=='boolean'||I[o.key].durability&&(!Number.isFinite(o.durability)||o.durability<0||o.durability>I[o.key].durability))bad();ids.add(o.uid);}
      if(r.serial<Math.max(0,...ids))bad();for(const [slot,id] of Object.entries(r.equipped))if(!slots[slot]||!ids.has(id)||I[object(r,id).key].kind!==slot)bad();
      if(r.loot.some(k=>typeof k!=='string'||!has(I,k))||r.bin_loot&&(!Array.isArray(r.bin_loot)||r.bin_loot.some(k=>typeof k!=='string'||!has(I,k))))bad();
      for(const o of r.options)if(!['business','camp','event','arena','bins'].includes(o.kind)||o.kind==='business'&&(!Number.isInteger(o.venue)||!D.businesses[o.venue])||!Number.isInteger(o.danger)||o.danger<1||o.danger>3)bad();
      if(r.phase==='briefing'&&(!Number.isInteger(r.pending_route)||!r.options[r.pending_route]||r.options[r.pending_route].kind!=='business'))bad();
      if(['combat','loot','incident'].includes(r.phase)&&(!r.encounter||!r.enemy||!Number.isFinite(r.enemy.hp)||!Number.isFinite(r.enemy.max_hp)||r.enemy.max_hp<=0||!Number.isFinite(r.enemy.attack)||!['attack','recover'].includes(r.enemy.intent)))bad();
      if(['combat','loot','incident'].includes(r.phase)){
        const o=r.encounter,e=r.enemy;
        if(!['business','arena'].includes(o.kind)||!Number.isInteger(o.danger)||o.danger<1||o.danger>3||o.kind==='business'&&(!Number.isInteger(o.venue)||!D.businesses[o.venue])||typeof e.name!=='string'||typeof e.boss!=='boolean'||e.hp<0||e.hp>e.max_hp||r.phase==='combat'&&e.hp===0)bad();
        if(o.kind==='business'&&(!plain(e.narrative)||['name','opening','pressure','recover','hit','done'].some(k=>typeof e.narrative[k]!=='string')))bad();
      }
      if(r.last_check&&(!plain(r.last_check)||!has(D.attributes,r.last_check.attribute)||!Number.isFinite(r.last_check.bonus)||!Number.isFinite(r.last_check.dc)||!Number.isInteger(r.last_check.roll)||r.last_check.roll<1||r.last_check.roll>20||!Number.isFinite(r.last_check.total)||typeof r.last_check.success!=='boolean'))bad();
      if(r.phase==='incident'&&!has(D.incidents,r.incident)||r.phase==='event'&&!has(D.events,r.event)||['bins','bin_loot'].includes(r.phase)&&!has(D.bins,r.bin_key))bad();
      if(r.basket&&(!Array.isArray(r.basket.uids)||!r.basket.uids.length||new Set(r.basket.uids).size!==r.basket.uids.length||r.basket.uids.some(id=>!ids.has(id))||!Number.isFinite(r.basket.ready_turn)))bad();
      for(const e of Object.values(r.effects))if(!Number.isFinite(e.power)||!Number.isFinite(e.until))bad();
      for(const m of r.digestion)if(typeof m.name!=='string'||!Number.isFinite(m.energy)||m.energy<0||!Number.isFinite(m.fat))bad();
      for(const v of r.violations)if(typeof v.title!=='string'||typeof v.rule!=='string'||typeof v.resolved!=='boolean')bad();
      for(const e of r.hygiene_log)if(!Number.isInteger(e.day)||!Number.isFinite(e.temperature))bad();
      for(const e of r.distribution_log)if(!has(D.channels,e.channel)||!Array.isArray(e.names)||e.names.some(n=>typeof n!=='string'))bad();
      if(r.log.some(n=>typeof n!=='string')||typeof r.character_name!=='string'||!r.attribute_dice||Object.keys(D.attributes).some(k=>!Array.isArray(r.attribute_dice[k])||r.attribute_dice[k].length!==4||r.attribute_dice[k].some(n=>!Number.isInteger(n)||n<1||n>6)))bad();
      if(typeof s.learn.name!=='string'||typeof s.learn.answered!=='boolean'||!Number.isFinite(s.learn.mistakes)||!['intro','quiz','agreement','pickup','verification','finish'].includes(s.learn.stage)||!Number.isInteger(s.learn.quiz)||s.learn.quiz<0||s.learn.quiz>D.learning.QUIZ.length||s.learn.stage==='quiz'&&s.learn.quiz>=D.learning.QUIZ.length||!Number.isInteger(s.learn.pickup)||s.learn.pickup<0||s.learn.pickup>D.learning.PICKUPS.length||s.learn.stage==='pickup'&&s.learn.pickup>=D.learning.PICKUPS.length||!Array.isArray(s.learn.log))bad();
      if(s.duel){const d=s.duel;if(!Array.isArray(d.players)||d.players.length!==2||![0,1].includes(d.turn)||![null,0,1].includes(d.winner)||!Array.isArray(d.log)||d.log.some(x=>typeof x!=='string'))bad();for(const p of d.players)if(typeof p.name!=='string'||!has(I,p.weapon)||I[p.weapon].kind!=='weapon'||![p.hp,p.stamina,p.potions].every(Number.isFinite)||p.hp<0||p.hp>100||p.stamina<0||p.stamina>40||p.potions<0||p.potions>2)bad();}
      return copy(s);
    }
    return {newRun,act,stats,weight,bonus,freshness,preview,spec,summary,chance,mod,briefing,eligible,reserved,newDuel,duel,newLearner,learn,validate,signed};
  }
  if(typeof module==='object'&&module.exports)module.exports=createEngine;else root.createFairteilerEngine=createEngine;
})(typeof globalThis!=='undefined'?globalThis:this);
