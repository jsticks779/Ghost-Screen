type Props = { small?: boolean }

export default function Logo({ small }: Props) {
  return (
    <img
      src="/logo.svg"
      alt="Ghost Screen"
      className={`${small ? "h-7 w-auto" : "h-20 w-auto"} animate-flag-wave`}
    />
  )
}
