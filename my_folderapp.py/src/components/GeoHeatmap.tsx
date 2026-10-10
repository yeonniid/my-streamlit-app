type Point={symbol:string;name:string;lat:number;lng:number;level:number}
type Props={points:Point[];active:string;onSelect:(symbol:string)=>void}
const positioned=(point:Point)=>({left:`${((point.lng+180)/360)*100}%`,top:`${((90-point.lat)/180)*100}%`})
export default function GeoHeatmap({points,active,onSelect}:Props){
 return <section className="heatmap-panel heatmap-3d">
  <div className="heatmap-head"><div><small>3D 지리 히트맵 · 교육용 이상 기후 관측</small><h2>고도 지형과 붉은 이상 영역을 눌러 거래 종목을 여세요</h2></div><span className="wind-key">↝ 실시간 바람 흐름</span></div>
  <div className="terrain-stage" aria-label="고도와 바람 흐름이 표시된 지리 히트맵">
   <div className="terrain-grid"/><div className="ridge ridge-a"/><div className="ridge ridge-b"/><div className="ridge ridge-c"/>
   <div className="wind-stream stream-a">↝</div><div className="wind-stream stream-b">↝</div><div className="wind-stream stream-c">↝</div>
   {points.map(point=><button key={point.symbol} className={'hotspot '+(point.symbol===active?'active':'')} style={positioned(point)} onClick={()=>onSelect(point.symbol)} aria-label={`${point.name} ${point.symbol} 종목 선택`}><span className="heat-core" style={{'--level':point.level} as React.CSSProperties}/><b>{point.name}</b><small>{point.symbol} · 고도 {point.level}</small></button>)}
   <div className="altitude altitude-high">▲ 고도 상승</div><div className="altitude altitude-low">▽ 저지대</div>
  </div>
  <div className="wind-flow"><span>서풍 이동</span><i>↝</i><span>산맥 상승기류</span><i>↝</i><span>인접 지역 연쇄 변동</span></div>
 </section>
}
