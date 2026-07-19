"use client";

import { FormEvent, ReactNode, useEffect, useState } from "react";
import { LogIn, UserPlus } from "lucide-react";
import {
  getStoredSession,
  login,
  onStoredSessionChange,
  register,
  storeSession,
} from "@/lib/api";
import type { AuthSession } from "@/types/auth";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";

type AuthGateProps = {
  children: (session: AuthSession, onSessionChange: (session: AuthSession) => void) => ReactNode;
};

export function AuthGate({ children }: AuthGateProps) {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [values, setValues] = useState({
    email: "",
    password: "",
    name: "",
    organization_name: "Nexalyze",
    workspace_name: "GrowthOS Workspace",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    window.queueMicrotask(() => setSession(getStoredSession()));
    return onStoredSessionChange(setSession);
  }, []);

  function update(key: keyof typeof values, value: string) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  function onSessionChange(nextSession: AuthSession) {
    storeSession(nextSession);
    setSession(nextSession);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const nextSession =
        mode === "login"
          ? await login({ email: values.email, password: values.password })
          : await register(values);
      setSession(nextSession);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to authenticate.",
      );
    } finally {
      setLoading(false);
    }
  }

  if (session) {
    return children(session, onSessionChange);
  }

  return (
    <main className="min-h-screen bg-[#070b14] px-4 py-10 text-slate-100">
      <div className="mx-auto flex min-h-[calc(100vh-5rem)] max-w-5xl items-center">
        <div className="grid w-full gap-8 lg:grid-cols-[1fr_420px]">
          <div className="flex flex-col justify-center">
            <p className="text-sm font-medium text-cyan-300">GrowthOS Platform</p>
            <h1 className="mt-3 max-w-2xl text-4xl font-semibold tracking-tight text-white">
              Secure workspace foundation for Nexalyze GrowthOS
            </h1>
            <p className="mt-4 max-w-xl text-sm leading-6 text-slate-400">
              Sign in to access workspace-scoped Brand Brain, Research Hub, and
              AI Content Studio workflows.
            </p>
          </div>
          <Card>
            <div className="flex rounded-lg border border-white/10 bg-slate-950/70 p-1">
              <button
                className={`flex-1 rounded-md px-3 py-2 text-sm font-semibold ${
                  mode === "login" ? "bg-cyan-400 text-slate-950" : "text-slate-300"
                }`}
                onClick={() => setMode("login")}
                type="button"
              >
                Login
              </button>
              <button
                className={`flex-1 rounded-md px-3 py-2 text-sm font-semibold ${
                  mode === "register" ? "bg-cyan-400 text-slate-950" : "text-slate-300"
                }`}
                onClick={() => setMode("register")}
                type="button"
              >
                Register
              </button>
            </div>
            <form className="mt-5 space-y-4" onSubmit={submit}>
              {mode === "register" ? (
                <Field
                  id="auth-name"
                  label="Name"
                  onChange={(value) => update("name", value)}
                  required
                  value={values.name}
                />
              ) : null}
              <Field
                id="auth-email"
                label="Email"
                onChange={(value) => update("email", value)}
                required
                value={values.email}
              />
              <Field
                id="auth-password"
                label="Password"
                onChange={(value) => update("password", value)}
                required
                type="password"
                value={values.password}
              />
              {mode === "register" ? (
                <>
                  <Field
                    id="auth-organization"
                    label="Organization"
                    onChange={(value) => update("organization_name", value)}
                    required
                    value={values.organization_name}
                  />
                  <Field
                    id="auth-workspace"
                    label="Workspace"
                    onChange={(value) => update("workspace_name", value)}
                    required
                    value={values.workspace_name}
                  />
                </>
              ) : null}
              {error ? (
                <p className="rounded-lg border border-red-400/25 bg-red-500/10 px-4 py-3 text-sm text-red-100">
                  {error}
                </p>
              ) : null}
              <Button
                disabled={loading}
                icon={mode === "login" ? LogIn : UserPlus}
                type="submit"
              >
                {loading
                  ? "Working"
                  : mode === "login"
                    ? "Login"
                    : "Create account"}
              </Button>
            </form>
          </Card>
        </div>
      </div>
    </main>
  );
}
