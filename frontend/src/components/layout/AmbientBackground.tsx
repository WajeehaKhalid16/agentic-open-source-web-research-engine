import { useReducedMotion } from 'framer-motion';

export function AmbientBackground() {
  const reduced = useReducedMotion();

  if (reduced) {
    return (
      <div
        aria-hidden="true"
        className="fixed inset-0 -z-10"
        style={{
          background:
            'radial-gradient(ellipse 80% 60% at 30% 40%, #FDE0B8 0%, #FFF7EC 60%, #FFF7EC 100%)',
        }}
      />
    );
  }

  return (
    <div aria-hidden="true" className="fixed inset-0 -z-10 overflow-hidden">
      <video
        muted
        autoPlay
        loop
        playsInline
        poster="/ambient-poster.jpg"
        className="absolute inset-0 w-full h-full object-cover opacity-30"
      >
        <source src="/ambient-bg.webm" type="video/webm" />
        <source src="/ambient-bg.mp4" type="video/mp4" />
      </video>
      <div
        className="absolute inset-0"
        style={{
          background:
            'linear-gradient(135deg, rgba(255,247,236,0.88) 0%, rgba(253,224,184,0.60) 50%, rgba(255,247,236,0.90) 100%)',
        }}
      />
    </div>
  );
}
