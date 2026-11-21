<script lang="ts">
  let scrollY = $state(0);
</script>

<svelte:window bind:scrollY />

<div class="hint" class:hidden={scrollY > 0} aria-hidden="true">
  <span>Scroll</span>
  <svg viewBox="0 0 24 24" width="20" height="20">
    <path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" />
  </svg>
</div>

<style>
  .hint {
    position: fixed;
    left: 50%;
    bottom: 1.5rem;
    translate: -50% 0;
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    color: var(--ink-soft);
    font-size: 0.8rem;
    letter-spacing: 0.05em;
    opacity: 0.5;
    pointer-events: none;
    transition: opacity 0.4s;
    animation: bob 2s ease-in-out infinite;
  }
  .hint.hidden {
    opacity: 0;
  }
  @keyframes bob {
    50% {
      transform: translateY(4px);
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .hint {
      animation: none;
    }
  }
</style>
