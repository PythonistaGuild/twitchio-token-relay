import type { Component, JSX } from "solid-js";

export type ParentProps<P = {}> = P & { children?: JSX.Element };
export type ParentComponent<P = {}> = Component<ParentProps<P>>;
