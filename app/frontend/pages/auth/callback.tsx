import { useEffect } from "react";
import { useRouter } from "next/router";
import { supabase } from "../../lib/supabaseClient";

export default function Callback() {
  const router = useRouter();
  useEffect(() => {
    (async () => {
      const { data } = await supabase.auth.getSession();
      const token = data.session?.access_token;
      if (token) localStorage.setItem("sb-access-token", token);
      router.replace("/"); // go home
    })();
  }, [router]);
  return <p style={{padding:24}}>Signing you in…</p>;
}
