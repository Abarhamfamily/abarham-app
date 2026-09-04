import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const typographyVariants = cva("", {
  variants: {
    variant: {
      h1: "text-4xl font-bold tracking-tight",
      h2: "text-3xl font-bold tracking-tight",
      h3: "text-2xl font-semibold tracking-tight",
      h4: "text-xl font-semibold tracking-tight",
      h5: "text-lg font-semibold tracking-tight",
      h6: "text-base font-semibold tracking-tight",
      p: "text-base leading-7",
      lead: "text-lg leading-7 text-muted-foreground",
      large: "text-lg leading-7",
      small: "text-sm leading-6 text-muted-foreground",
      muted: "text-sm leading-6 text-muted-foreground",
      blockquote: "text-lg leading-7 border-l-4 border-primary pl-4 italic text-muted-foreground",
      code: "text-sm font-mono bg-muted px-1.5 py-0.5 rounded",
      link: "text-primary underline-offset-4 hover:underline",
    },
  },
  defaultVariants: {
    variant: "p",
  },
})

export interface TypographyProps
  extends React.HTMLAttributes<HTMLElement>,
    VariantProps<typeof typographyVariants> {
  as?: "h1" | "h2" | "h3" | "h4" | "h5" | "h6" | "p" | "span" | "div" | "a" | "blockquote" | "code" | "small"
}

const Typography = React.forwardRef<unknown, TypographyProps>(
  ({ className, variant, as: Component = "p", ...props }, ref) => {
    return React.createElement(Component, {
      ref,
      className: cn(typographyVariants({ variant, className })),
      ...props,
    })
  }
)
Typography.displayName = "Typography"

export { Typography, typographyVariants }