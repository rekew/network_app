import * as React from "react"
import { Slot } from "@radix-ui/react-slot"

type Variant = "default" | "destructive" | "outline" | "secondary" | "ghost" | "link"
type Size = "default" | "sm" | "lg" | "icon"

const variantStyles: Record<Variant, React.CSSProperties> = {
  default:     { background: "#2196f3", color: "#fff" },
  destructive: { background: "#dc2626", color: "#fff" },
  outline:     { background: "transparent", color: "#8ba4b8", border: "1.5px solid #2b3a4a" },
  secondary:   { background: "#1e2c3a", color: "#e8f0f8", border: "1px solid #2b3a4a" },
  ghost:       { background: "transparent", color: "#8ba4b8" },
  link:        { background: "transparent", color: "#2196f3", textDecoration: "underline", padding: 0 },
}

const sizeStyles: Record<Size, React.CSSProperties> = {
  default: { height: "40px", padding: "0 16px", fontSize: "14px" },
  sm:      { height: "36px", padding: "0 12px", fontSize: "13px" },
  lg:      { height: "44px", padding: "0 24px", fontSize: "15px" },
  icon:    { height: "40px", width: "40px", padding: 0 },
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "default", size = "default", asChild = false, style, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        ref={ref}
        style={{
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "7px",
          borderRadius: "10px",
          fontWeight: 600,
          fontFamily: "inherit",
          cursor: "pointer",
          border: "none",
          transition: "all 0.2s",
          textDecoration: "none",
          ...variantStyles[variant],
          ...sizeStyles[size],
          ...style,
        }}
        onMouseEnter={e => {
          const el = e.currentTarget as HTMLElement
          if (variant === "default")  el.style.background = "#1e88e5"
          if (variant === "destructive") el.style.background = "#b91c1c"
          if (variant === "outline") { el.style.borderColor = "#2196f3"; el.style.color = "#2196f3" }
          if (variant === "secondary") el.style.borderColor = "#4a6278"
          if (variant === "ghost") el.style.background = "#1e2c3a"
        }}
        onMouseLeave={e => {
          const el = e.currentTarget as HTMLElement
          if (variant === "default")  el.style.background = "#2196f3"
          if (variant === "destructive") el.style.background = "#dc2626"
          if (variant === "outline") { el.style.borderColor = "#2b3a4a"; el.style.color = "#8ba4b8" }
          if (variant === "secondary") el.style.borderColor = "#2b3a4a"
          if (variant === "ghost") el.style.background = "transparent"
        }}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }