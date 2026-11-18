// 화면 공통 부품. 화면 파일에서는 색·크기를 새로 정하지 말고 이것을 쓴다.
// 규칙: 이모지 없음, 굵기는 600(semibold)·700(bold)까지, 모서리 12px, 그림자 대신 1px 선.
import React from "react";
import {
  ActivityIndicator,
  ScrollView,
  Text,
  TouchableOpacity,
  View,
  ViewStyle,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export const colors = {
  ink: "#18181B",
  muted: "#71717A",
  line: "#E7E7E4",
  canvas: "#F6F6F4",
  brand: "#1F6F54",
  brandSoft: "#E9F2EE",
  danger: "#B42318",
};

type Children = { children?: React.ReactNode };

export function Screen({
  children,
  scroll = true,
  footer,
  edges = ["bottom"],
}: Children & { scroll?: boolean; footer?: React.ReactNode; edges?: ("top" | "bottom")[] }) {
  return (
    <SafeAreaView className="flex-1 bg-white" edges={edges}>
      {scroll ? (
        <ScrollView className="flex-1" contentContainerStyle={{ padding: 20, paddingBottom: 40 }} showsVerticalScrollIndicator={false}>
          {children}
        </ScrollView>
      ) : (
        <View className="flex-1">{children}</View>
      )}
      {footer ? <View className="px-5 pt-3 pb-5 border-t border-line bg-white">{footer}</View> : null}
    </SafeAreaView>
  );
}

export function Title({ children, sub }: Children & { sub?: string }) {
  return (
    <View className="mb-6">
      <Text className="text-[24px] leading-8 font-bold text-ink">{children}</Text>
      {sub ? <Text className="text-[14px] leading-5 text-zinc-500 mt-1.5">{sub}</Text> : null}
    </View>
  );
}

export function Label({ children, right }: Children & { right?: React.ReactNode }) {
  return (
    <View className="flex-row justify-between items-center mb-2">
      <Text className="text-[13px] font-semibold text-zinc-500">{children}</Text>
      {right}
    </View>
  );
}

export function Section({ children, label, right, style }: Children & { label?: string; right?: React.ReactNode; style?: ViewStyle }) {
  return (
    <View className="mb-6" style={style}>
      {label ? <Label right={right}>{label}</Label> : null}
      {children}
    </View>
  );
}

export function Card({ children, tone = "plain", style }: Children & { tone?: "plain" | "muted" | "brand"; style?: ViewStyle }) {
  const bg = tone === "muted" ? "bg-canvas border-canvas" : tone === "brand" ? "bg-brand-soft border-brand-soft" : "bg-white border-line";
  return (
    <View className={`rounded-xl border p-4 ${bg}`} style={style}>
      {children}
    </View>
  );
}

export function Button({
  label,
  onPress,
  variant = "primary",
  disabled,
  loading,
}: {
  label: string;
  onPress?: () => void;
  variant?: "primary" | "secondary" | "ghost" | "danger";
  disabled?: boolean;
  loading?: boolean;
}) {
  const box = {
    primary: "bg-ink",
    secondary: "bg-white border border-line",
    ghost: "",
    danger: "bg-white border border-line",
  }[variant];
  const text = {
    primary: "text-white",
    secondary: "text-ink",
    ghost: "text-zinc-500",
    danger: "text-danger",
  }[variant];
  const off = disabled || loading;
  return (
    <TouchableOpacity
      onPress={off ? undefined : onPress}
      activeOpacity={0.75}
      accessibilityRole="button"
      className={`h-12 rounded-xl items-center justify-center px-4 ${box} ${off ? "opacity-40" : ""}`}
    >
      {loading ? (
        <ActivityIndicator color={variant === "primary" ? "#fff" : colors.ink} />
      ) : (
        <Text className={`text-[15px] font-semibold ${text}`}>{label}</Text>
      )}
    </TouchableOpacity>
  );
}

// 여러 값 가운데 하나 고르기. 칸이 많으면 줄을 바꾼다.
export function Segmented<T extends string | number>({
  options,
  value,
  onChange,
  wrap = false,
}: {
  options: { label: string; value: T }[];
  value: T;
  onChange: (v: T) => void;
  wrap?: boolean;
}) {
  if (wrap) {
    return (
      <View className="flex-row flex-wrap -m-1">
        {options.map((o) => (
          <Chip key={String(o.value)} label={o.label} selected={o.value === value} onPress={() => onChange(o.value)} />
        ))}
      </View>
    );
  }
  return (
    <View className="flex-row bg-canvas rounded-xl p-1">
      {options.map((o) => {
        const on = o.value === value;
        return (
          <TouchableOpacity activeOpacity={0.75}
            key={String(o.value)}
            onPress={() => onChange(o.value)}
            accessibilityRole="button"
            accessibilityState={{ selected: on }}
            className={`flex-1 h-10 rounded-lg items-center justify-center ${on ? "bg-white border border-line" : ""}`}
          >
            <Text className={`text-[14px] ${on ? "font-semibold text-ink" : "text-zinc-500"}`}>{o.label}</Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

export function Chip({ label, selected, onPress, tone = "brand" }: { label: string; selected?: boolean; onPress?: () => void; tone?: "brand" | "danger" }) {
  const on = tone === "danger" ? "bg-danger border-danger" : "bg-brand border-brand";
  return (
    <TouchableOpacity activeOpacity={0.75}
      onPress={onPress}
      accessibilityRole="button"
      accessibilityState={{ selected: !!selected }}
      className={`m-1 h-9 px-3.5 rounded-lg border items-center justify-center ${selected ? on : "bg-white border-line"}`}
    >
      <Text className={`text-[14px] ${selected ? "text-white font-semibold" : "text-ink"}`}>{label}</Text>
    </TouchableOpacity>
  );
}

// 「항목 - 값」 한 줄. onPress 가 있으면 누를 수 있다.
export function Row({ label, value, onPress, last }: { label: string; value?: React.ReactNode; onPress?: () => void; last?: boolean }) {
  const body = (
    <View className={`flex-row justify-between items-center py-3.5 ${last ? "" : "border-b border-line"}`}>
      <Text className="text-[15px] text-zinc-500">{label}</Text>
      {typeof value === "string" || typeof value === "number" ? (
        <Text className="text-[15px] font-semibold text-ink">{value}</Text>
      ) : (
        value
      )}
    </View>
  );
  return onPress ? <TouchableOpacity activeOpacity={0.75} onPress={onPress}>{body}</TouchableOpacity> : body;
}

export function Stat({ label, value, unit }: { label: string; value: string | number; unit?: string }) {
  return (
    <View className="flex-1">
      <Text className="text-[13px] text-zinc-500 mb-1">{label}</Text>
      <Text className="text-[20px] font-bold text-ink">
        {value}
        {unit ? <Text className="text-[14px] font-medium text-zinc-500"> {unit}</Text> : null}
      </Text>
    </View>
  );
}

export function Loading() {
  return (
    <View className="flex-1 items-center justify-center bg-white">
      <ActivityIndicator color={colors.ink} />
    </View>
  );
}

// Claude 답변의 간단한 마크다운(제목 #, 굵게 **, 코드 `)과 이모지를 걷어 내고 문단으로 보여 준다.
// 「1. 운동 설명: 내용」처럼 제목과 내용이 한 줄이면 제목만 굵게 한다.
let EMOJI: RegExp | null = null;
try {
  EMOJI = new RegExp("[\\p{Extended_Pictographic}\\uFE0F\\u200D]", "gu");
} catch {
  EMOJI = null; // 유니코드 속성 정규식을 못 쓰는 엔진이면 이모지는 그대로 둔다
}

export function PlainText({ text }: { text: string }) {
  const lines = (text || "")
    .replace(/\r/g, "")
    .split("\n")
    .map((l) => {
      let t = l.replace(/^#+\s*/, "").replace(/\*\*/g, "").replace(/`/g, "");
      if (EMOJI) t = t.replace(EMOJI, "");
      return t.replace(/\s{2,}/g, " ").trimEnd();
    });
  return (
    <View>
      {lines.map((l, i) => {
        if (!l.trim()) return <View key={i} className="h-2" />;
        const head = l.match(/^(\d+\.\s[^:：]{1,24}[:：])\s*(.*)$/);
        if (head) {
          return (
            <Text key={i} className="text-[15px] leading-6 text-zinc-700 mt-2">
              <Text className="font-semibold text-ink">{head[1]}</Text>
              {head[2] ? " " + head[2] : ""}
            </Text>
          );
        }
        // 「1. 운동 설명」처럼 번호와 짧은 제목만 있는 줄
        if (/^\d+\.\s\S.{0,20}$/.test(l.trim())) {
          return (
            <Text key={i} className="text-[15px] leading-6 font-semibold text-ink mt-3">
              {l.trim()}
            </Text>
          );
        }
        const bullet = /^\s*[-*·]\s/.test(l);
        return (
          <Text key={i} className={`text-[15px] leading-6 text-zinc-700 ${bullet ? "pl-3" : ""}`}>
            {bullet ? "· " + l.replace(/^\s*[-*·]\s/, "") : l}
          </Text>
        );
      })}
    </View>
  );
}
