// API preference (v1 | v2) for the Daemon docs, modelled on Vue's "API
// Preference" switch. The choice lives in localStorage and on
// <html data-api>; `?api=v1|v2` on a URL preselects it. Both variants of a
// page are rendered; CSS hides the one that is not chosen.
import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import type { MouseEvent, ReactNode } from 'react';
import { usePageData } from '@rspress/core/runtime';
import './ApiPreference.css';

export type ApiStyle = 'v1' | 'v2';
const STORAGE_KEY = 'aiod-api-preference';
const DEFAULT_STYLE: ApiStyle = 'v1';

function initialStyle(): ApiStyle {
  if (typeof window === 'undefined') return DEFAULT_STYLE;
  const fromQuery = new URLSearchParams(window.location.search).get('api');
  if (fromQuery === 'v1' || fromQuery === 'v2') return fromQuery;
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === 'v1' || stored === 'v2') return stored;
  } catch {
    // storage unavailable: fall through to the default
  }
  return DEFAULT_STYLE;
}

const ApiPreferenceContext = createContext<{ api: ApiStyle; setApi: (next: ApiStyle) => void }>({
  api: DEFAULT_STYLE,
  setApi: () => {},
});

export function ApiPreferenceProvider({ children }: { children: ReactNode }) {
  const [api, setApiState] = useState<ApiStyle>(DEFAULT_STYLE);
  useEffect(() => {
    setApiState(initialStyle());
  }, []);
  useEffect(() => {
    document.documentElement.dataset.api = api;
  }, [api]);
  const setApi = useCallback((next: ApiStyle) => {
    setApiState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // storage unavailable: the choice lasts for this page only
    }
  }, []);
  return <ApiPreferenceContext.Provider value={{ api, setApi }}>{children}</ApiPreferenceContext.Provider>;
}

export function useApiPreference() {
  return useContext(ApiPreferenceContext);
}

const TEXT = {
  en: {
    title: 'API Preference',
    hint: 'The API style defaults to v1. Some pages show different examples for each style; use this switch to change it.',
    more: 'Learn more',
    moreHref: '/daemon/start/migration',
    when: (when: string) => `When ${when}, switch to v2: `,
  },
  zh: {
    title: 'API 偏好',
    hint: 'API 风格默认为 v1。部分页面会按风格显示不同的示例，用这个开关切换。',
    more: '了解更多',
    moreHref: '/zh/daemon/start/migration',
    // A space between a Latin word and 时, as the rest of the docs set it.
    when: (when: string) => `需要${when}${/[A-Za-z0-9)]$/.test(when) ? ' ' : ''}时，切到 v2：`,
  },
};

function usePageLang(): 'en' | 'zh' {
  const { page } = usePageData() as { page?: { lang?: string } };
  return page?.lang === 'zh' ? 'zh' : 'en';
}

export function ApiPreferenceSwitch() {
  const { page } = usePageData() as { page?: { routePath?: string } };
  const lang = usePageLang();
  const { api, setApi } = useApiPreference();
  const [open, setOpen] = useState(false);
  const [caretLeft, setCaretLeft] = useState(0);
  if (!/\/daemon\//.test(page?.routePath ?? '')) return null;
  const t = TEXT[lang];
  // The tooltip spans the card so the sidebar cannot clip it; the caret
  // is moved under the ? whenever it opens.
  const show = (event: MouseEvent<HTMLButtonElement>) => {
    const card = event.currentTarget.closest('.aiod-api-pref') as HTMLElement | null;
    if (card) {
      const help = event.currentTarget.getBoundingClientRect();
      const box = card.getBoundingClientRect();
      setCaretLeft(help.left - box.left + help.width / 2);
    }
    setOpen(true);
  };
  return (
    <div className="aiod-api-pref" onMouseLeave={() => setOpen(false)}>
      <div className="aiod-api-pref-title">{t.title}</div>
      <div className="aiod-api-pref-row">
        <button type="button" className={`aiod-api-label${api === 'v1' ? ' is-active' : ''}`} onClick={() => setApi('v1')}>
          v1
        </button>
        <button
          type="button"
          role="switch"
          aria-checked={api === 'v2'}
          aria-label="API style"
          className={`aiod-api-toggle is-${api}`}
          onClick={() => setApi(api === 'v1' ? 'v2' : 'v1')}
        >
          <span className="aiod-api-knob" />
        </button>
        <button type="button" className={`aiod-api-label${api === 'v2' ? ' is-active' : ''}`} onClick={() => setApi('v2')}>
          v2
        </button>
        <button
          type="button"
          className={`aiod-api-help${open ? ' is-open' : ''}`}
          aria-label={t.more}
          onMouseEnter={show}
          onClick={(event) => (open ? setOpen(false) : show(event))}
        >
          ?
        </button>
      </div>
      {open && (
        <div className="aiod-api-pop" role="tooltip" style={{ '--aiod-caret-left': `${caretLeft}px` } as React.CSSProperties}>
          <p>{t.hint}</p>
          <a href={t.moreHref}>{t.more}</a>
        </div>
      )}
    </div>
  );
}

export function ApiV1({ children }: { children: ReactNode }) {
  return <div className="api-block api-v1">{children}</div>;
}

export function ApiV2({ children }: { children: ReactNode }) {
  return <div className="api-block api-v2">{children}</div>;
}

// Inline counterparts of ApiV1 / ApiV2, for route mentions inside a sentence.
// Both variants render and CSS shows only the chosen API style, like blocks.
export function ApiInlineV1({ children }: { children: ReactNode }) {
  return <span className="api-inline api-inline-v1">{children}</span>;
}

export function ApiInlineV2({ children }: { children: ReactNode }) {
  return <span className="api-inline api-inline-v2">{children}</span>;
}

// A one-line pointer shown only in v1 mode: "When <when>, switch to v2:
// <route>". Clicking the route switches the preference and scrolls to the
// next v2 block, which is where the example for that route lives.
export function UseV2({ when, route, children }: { when: string; route: string; children?: ReactNode }) {
  const { setApi } = useApiPreference();
  const lang = usePageLang();
  const onClick = (event: MouseEvent<HTMLButtonElement>) => {
    const hint = event.currentTarget.closest('.api-hint-v2');
    setApi('v2');
    requestAnimationFrame(() => {
      // The v2 example for this route is the next v2 block in the same
      // section; past the next heading there is none, so stay in place.
      let node = hint?.nextElementSibling ?? null;
      while (node && !node.classList.contains('api-v2') && !/^H[1-6]$/.test(node.tagName)) {
        node = node.nextElementSibling;
      }
      const target = node?.classList.contains('api-v2') ? node : hint;
      target?.scrollIntoView({ block: 'start', behavior: 'smooth' });
    });
  };
  return (
    <p className="api-hint-v2">
      {TEXT[lang].when(when)}
      <button type="button" className="aiod-api-link" onClick={onClick}>
        <code>{route}</code>
      </button>
      {children ? <> {children}</> : null}
    </p>
  );
}
