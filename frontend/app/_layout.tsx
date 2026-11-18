import { Stack } from "expo-router";
import { Platform, View } from "react-native";
import "../output.css";

// 웹에서는 휴대폰 폭(최대 480px)으로 가운데 둔다. 넓은 화면에서 늘어지지 않고, 좁은 화면에서 넘치지 않는다.
const webFrame =
  Platform.OS === "web"
    ? { flex: 1, width: "100%" as const, maxWidth: 480, alignSelf: "center" as const, backgroundColor: "#fff", overflow: "hidden" as const }
    : { flex: 1 };

export default function Layout() {
  return (
    <View style={{ flex: 1, backgroundColor: "#F6F6F4" }}>
      <View style={webFrame}>
        <Stack
          screenOptions={{
            headerStyle: { backgroundColor: "#fff" },
            headerTintColor: "#18181B",
            headerTitleStyle: { fontWeight: "600", fontSize: 16 },
            headerShadowVisible: false,
            headerBackTitle: "",
            contentStyle: { backgroundColor: "#fff" },
          }}
        />
      </View>
    </View>
  );
}
