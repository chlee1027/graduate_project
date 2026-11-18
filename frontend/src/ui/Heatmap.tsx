// 잔디 차트: 최근 몇 주를 하루 한 칸(세로 월~일, 가로 주)으로 그리고 운동한 분 수로 칠한다.
import React, { useMemo, useState } from "react";
import { Text, TouchableOpacity, View } from "react-native";

export type HeatDay = { date: string; count: number; minutes: number };

// 0분, 1~14, 15~29, 30~44, 45분 이상
const LEVEL_COLORS = ["#EFEFEC", "#CFE3D9", "#93BFA9", "#4F937A", "#1F6F54"];
const DAY_NAMES = ["월", "화", "수", "목", "금", "토", "일"];
const GAP = 3;
const LABEL_W = 18;

export function level(day: HeatDay | undefined): number {
  if (!day || !day.count) return 0;
  const m = day.minutes || 0;
  if (m >= 45) return 4;
  if (m >= 30) return 3;
  if (m >= 15) return 2;
  return 1;
}

function parse(d: string) {
  const [y, m, dd] = d.split("-").map(Number);
  return { y, m, d: dd };
}

export function Heatmap({ days, weeks }: { days: HeatDay[]; weeks: number }) {
  const [width, setWidth] = useState(0);
  const [selected, setSelected] = useState<number>(days.length - 1);

  const cell = width ? Math.max(8, Math.min(18, Math.floor((width - LABEL_W - GAP * (weeks - 1)) / weeks))) : 0;
  const step = cell + GAP;

  // 열(주)마다 그 주 첫날의 달. 달이 바뀌는 열 위에 「n월」. 앞 글자와 3열 안이면 건너뛴다.
  const monthLabels = useMemo(() => {
    const out: { col: number; text: string }[] = [];
    let lastMonth = -1;
    let lastCol = -10;
    for (let c = 0; c < weeks; c++) {
      const first = days[c * 7];
      if (!first) break;
      const { m } = parse(first.date);
      if (m !== lastMonth) {
        if (c - lastCol >= 3) {
          out.push({ col: c, text: `${m}월` });
          lastCol = c;
        }
        lastMonth = m;
      }
    }
    return out;
  }, [days, weeks]);

  const sel = days[selected];
  const selText = sel
    ? (() => {
        const { m, d } = parse(sel.date);
        const dow = DAY_NAMES[selected % 7];
        return sel.count ? `${m}월 ${d}일 (${dow}) · ${sel.count}번, ${sel.minutes}분` : `${m}월 ${d}일 (${dow}) · 기록 없음`;
      })()
    : "";

  return (
    <View onLayout={(e) => setWidth(e.nativeEvent.layout.width)}>
      {cell ? (
        <>
          <View style={{ height: 16, marginLeft: LABEL_W, position: "relative" }}>
            {monthLabels.map((l) => (
              <Text key={l.col} className="text-[11px] text-zinc-500" style={{ position: "absolute", left: l.col * step }}>
                {l.text}
              </Text>
            ))}
          </View>
          <View className="flex-row">
            <View style={{ width: LABEL_W }}>
              {DAY_NAMES.map((n, r) => (
                <Text
                  key={n}
                  className="text-[10px] text-zinc-400"
                  style={{ height: cell, lineHeight: cell, marginBottom: r < 6 ? GAP : 0, opacity: r % 2 === 0 ? 1 : 0 }}
                >
                  {n}
                </Text>
              ))}
            </View>
            {Array.from({ length: weeks }, (_, c) => (
              <View key={c} style={{ marginRight: c < weeks - 1 ? GAP : 0 }}>
                {Array.from({ length: 7 }, (_, r) => {
                  const i = c * 7 + r;
                  const day = days[i];
                  if (!day) return <View key={r} style={{ width: cell, height: cell, marginBottom: r < 6 ? GAP : 0 }} />;
                  const on = i === selected;
                  return (
                    <TouchableOpacity
                      key={r}
                      activeOpacity={0.7}
                      onPress={() => setSelected(i)}
                      accessibilityLabel={day.date + (day.count ? ` ${day.minutes}분` : " 기록 없음")}
                      style={{
                        width: cell,
                        height: cell,
                        marginBottom: r < 6 ? GAP : 0,
                        borderRadius: 3,
                        backgroundColor: LEVEL_COLORS[level(day)],
                        borderWidth: on ? 1.5 : 0,
                        borderColor: "#18181B",
                      }}
                    />
                  );
                })}
              </View>
            ))}
          </View>
          <View className="flex-row justify-between items-center mt-3">
            <Text className="text-[12px] text-zinc-600">{selText}</Text>
            <View className="flex-row items-center">
              <Text className="text-[11px] text-zinc-400 mr-1">적음</Text>
              {LEVEL_COLORS.map((c) => (
                <View key={c} style={{ width: 10, height: 10, borderRadius: 2, backgroundColor: c, marginLeft: 2 }} />
              ))}
              <Text className="text-[11px] text-zinc-400 ml-1">많음</Text>
            </View>
          </View>
        </>
      ) : null}
    </View>
  );
}
