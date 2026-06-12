"use client";
import * as React from "react";
import { CalendarDays, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface DatePickerProps { value: string; onChange: (value: string) => void; id?: string; }
const DAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];

function todayDate(): Date { const d = new Date(); d.setHours(0,0,0,0); return d; }

export function DatePicker({ value, onChange, id }: DatePickerProps) {
  const [open, setOpen] = React.useState(false);
  const [mounted, setMounted] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);
  const selected = value ? new Date(value + "T12:00:00") : (mounted ? new Date() : new Date(0));
  const [viewYear, setViewYear] = React.useState(() => selected.getFullYear() || new Date().getFullYear());
  const [viewMonth, setViewMonth] = React.useState(() => selected.getMonth() || new Date().getMonth());

  React.useEffect(() => { setMounted(true); }, []);

  React.useEffect(() => {
    function handleClick(e: MouseEvent) { if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false); }
    if (open) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  const today = mounted ? todayDate() : new Date(0);
  const daysInMonth = (y:number,m:number) => new Date(y,m+1,0).getDate();
  const firstDay = (y:number,m:number) => new Date(y,m,1).getDay();
  const selectDate = (day:number) => { const d = new Date(viewYear,viewMonth,day); onChange(d.toISOString().slice(0,10)); setOpen(false); };
  const prev = () => { if(viewMonth===0){setViewMonth(11);setViewYear(viewYear-1)}else{setViewMonth(viewMonth-1)} };
  const next = () => { if(viewMonth===11){setViewMonth(0);setViewYear(viewYear+1)}else{setViewMonth(viewMonth+1)} };

  const total = daysInMonth(viewYear,viewMonth);
  const start = firstDay(viewYear,viewMonth);
  const cells: (number|null)[] = [];
  for(let i=0;i<start;i++) cells.push(null);
  for(let d=1;d<=total;d++) cells.push(d);

  const formatted = mounted
    ? selected.toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric",year:"numeric"})
    : value ? new Date(value + "T12:00:00").toISOString().slice(0,10) : "Select date";

  return (
    <div ref={ref} className="relative">
      <button id={id} type="button" onClick={()=>setOpen(!open)} className={cn("flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left font-mono text-sm transition-all duration-200","border-card-border bg-white/[0.03] text-foreground hover:border-white/15 focus:outline-none focus:ring-2 focus:ring-accent/40",open&&"border-accent/40")}>
        <CalendarDays className="size-4 text-accent shrink-0" /><span>{formatted}</span>
      </button>
      {open && (
        <div className="absolute left-0 top-full z-50 mt-2 w-[280px] animate-scale-in origin-top">
          <div className="rounded-2xl border border-white/[0.08] bg-[#0d1520] p-4 shadow-2xl shadow-black/50 backdrop-blur-2xl">
            <div className="flex items-center justify-between mb-3">
              <button type="button" onClick={prev} className="flex size-7 items-center justify-center rounded-lg text-faint hover:bg-white/[0.06] hover:text-foreground"><ChevronLeft className="size-4" /></button>
              <span className="font-display text-sm font-semibold text-foreground">{MONTHS[viewMonth]} {viewYear}</span>
              <button type="button" onClick={next} className="flex size-7 items-center justify-center rounded-lg text-faint hover:bg-white/[0.06] hover:text-foreground"><ChevronRight className="size-4" /></button>
            </div>
            <div className="grid grid-cols-7 mb-1">{DAYS.map(d=><span key={d} className="text-center font-mono text-[10px] uppercase tracking-wider text-faint py-1">{d}</span>)}</div>
            <div className="grid grid-cols-7 gap-0.5">
              {cells.map((day,i)=>{
                if(day===null) return <div key={`e${i}`} className="aspect-square" />;
                const date=new Date(viewYear,viewMonth,day);date.setHours(0,0,0,0);
                const isToday=mounted && date.getTime()===today.getTime();
                const isSel=day===selected.getDate()&&viewMonth===selected.getMonth()&&viewYear===selected.getFullYear();
                const isPast=mounted && date.getTime()<today.getTime();
                return <button key={day} type="button" disabled={isPast} onClick={()=>selectDate(day)} className={cn("aspect-square flex items-center justify-center rounded-lg font-mono text-xs transition-all",isSel&&"bg-accent text-black font-semibold shadow-[0_0_12px_-2px_var(--accent)]",!isSel&&!isPast&&"text-foreground hover:bg-white/[0.08]",isPast&&"text-faint/30 cursor-default",isToday&&!isSel&&"border border-accent/40 text-accent")}>{day}</button>;
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
