const CustomTooltip = ({ active, payload, label, isDark }) => {
  if (active && payload && payload.length) {
    return (
      <div className={`${isDark ? 'bg-[#05080f]/90 border-white/10' : 'bg-white/90 border-black/10 shadow-black/5'} backdrop-blur-xl p-3 rounded-lg border shadow-xl`}>
        <p className={`${isDark ? 'text-slate-300' : 'text-slate-700'} font-semibold mb-1`}>{label}</p>
        {payload[0] && (
          <p className="text-[#00e5a0] text-sm">PM2.5: <span className={`font-mono ${isDark ? 'text-white' : 'text-black'}`}>{payload[0].value} µg/m³</span></p>
        )}
        {payload[1] && (
          <p className="text-[#f87171] text-sm">Risk Index: <span className={`font-mono ${isDark ? 'text-white' : 'text-black'}`}>{payload[1].value}</span></p>
        )}
      </div>
    );
  }
  return null;
};

export default CustomTooltip;
