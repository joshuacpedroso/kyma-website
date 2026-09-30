/* Kyma Concierge — assistente virtual com efeito de digitação.
   Roda 100% no navegador: entende intenções por palavras-chave e
   encaminha o lead para o WhatsApp com a conversa resumida. */
(() => {
  const K = window.KYMA;
  if (!K) return;
  const d = document;
  const root = d.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = {
    get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* sem storage */ } }
  };

  const P = Object.fromEntries(K.projects.map(p => [p.slug, p]));
  const launches = K.projects.filter(p => p.status === 'lancamento');
  const pageProject = P[d.body.dataset.project] || null;

  const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
  const esc = s => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = s => esc(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
  const wa = msg => `https://wa.me/${K.whatsapp}?text=${encodeURIComponent(msg)}`;
  const sleep = ms => new Promise(r => setTimeout(r, reduce ? 0 : ms));
  const pick = arr => arr[Math.floor(Math.random() * arr.length)];

  const icon = {
    chat: '<svg class="i-chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.4-4.9A8 8 0 1 1 21 12z"/><path d="M8.5 11h.01M12 11h.01M15.5 11h.01" stroke-width="2.4"/></svg>',
    close: '<svg class="i-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    wa: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.4-.2z"/></svg>'
  };

  /* ---------- DOM ---------- */
  const launch = d.createElement('button');
  launch.className = 'kc-launch';
  launch.type = 'button';
  launch.setAttribute('aria-label', 'Abrir chat com a assistente virtual');
  launch.setAttribute('aria-expanded', 'false');
  launch.setAttribute('aria-controls', 'kc-panel');
  launch.innerHTML = icon.chat + icon.close + '<span class="kc-launch__dot"></span>';

  const teaser = d.createElement('div');
  teaser.className = 'kc-teaser';
  teaser.innerHTML = `<b>KYMA · CONCIERGE</b><span class="kc-teaser__t"></span><button class="kc-teaser__x" type="button" aria-label="Dispensar">${icon.x}</button>`;

  const panel = d.createElement('section');
  panel.className = 'kc-panel';
  panel.id = 'kc-panel';
  panel.setAttribute('aria-label', 'Chat com a assistente virtual da Kyma');
  panel.innerHTML = `
    <header class="kc-head">
      <div class="kc-avatar" aria-hidden="true">K</div>
      <div class="kc-head__t"><b>Kyma Concierge</b><span class="kc-status">Assistente virtual · online</span></div>
      <a href="${wa('Olá! Vim pelo site da Kyma e gostaria de falar com um corretor.')}" target="_blank" rel="noopener" aria-label="Falar no WhatsApp">${icon.wa}</a>
    </header>
    <div class="kc-body" role="log" aria-live="polite"><p class="kc-day">Hoje</p></div>
    <footer class="kc-foot">
      <form class="kc-form" autocomplete="off">
        <label class="sr-only" for="kc-input">Digite sua mensagem</label>
        <input id="kc-input" type="text" placeholder="Escreva sua mensagem…" maxlength="300">
        <button type="submit" aria-label="Enviar" disabled>${icon.send}</button>
      </form>
      <p class="kc-legal">Assistente virtual · respostas automáticas</p>
    </footer>`;
  d.body.append(teaser, panel, launch);

  const body = panel.querySelector('.kc-body');
  const form = panel.querySelector('.kc-form');
  const input = panel.querySelector('input');
  const sendBtn = panel.querySelector('button[type="submit"]');
  const status = panel.querySelector('.kc-status');

  const state = { name: null, awaiting: 'name', interest: null, period: null, started: false };

  /* ---------- Motor de mensagens ---------- */
  let queue = Promise.resolve();
  const scroll = () => { body.scrollTop = body.scrollHeight; };
  const enqueue = fn => (queue = queue.then(fn).catch(() => {}));

  const typeInto = (el, text) => new Promise(res => {
    if (reduce) { el.innerHTML = fmt(text); scroll(); res(); return; }
    el.classList.add('is-typing');
    let i = 0;
    const speed = text.length > 180 ? 7 : 13;
    const tick = () => {
      i = Math.min(text.length, i + (Math.random() < 0.25 ? 3 : 2));
      el.textContent = text.slice(0, i);
      scroll();
      if (i < text.length) {
        const ch = text[i - 1];
        const pause = /[.!?]/.test(ch) ? 180 : /[,:]/.test(ch) ? 70 : 0;
        setTimeout(tick, speed + Math.random() * 16 + pause);
      } else {
        el.classList.remove('is-typing');
        el.innerHTML = fmt(text);
        scroll();
        res();
      }
    };
    tick();
  });

  const showTyping = async ms => {
    const t = d.createElement('div');
    t.className = 'kc-typing';
    t.setAttribute('aria-label', 'Digitando');
    t.innerHTML = '<i></i><i></i><i></i>';
    body.append(t);
    status.textContent = 'digitando…';
    scroll();
    await sleep(ms);
    t.remove();
    status.textContent = 'Assistente virtual · online';
  };

  const say = (text, extra = {}) => enqueue(async () => {
    await showTyping(Math.min(1500, 450 + text.length * 9));
    const m = d.createElement('div');
    m.className = 'kc-msg kc-msg--bot';
    body.append(m);
    await typeInto(m, text);
    if (extra.cards) { renderCards(extra.cards); await sleep(250); }
    if (extra.cta) { renderCta(extra.cta); await sleep(200); }
    if (extra.chips) renderChips(extra.chips);
    scroll();
  });

  const renderCards = slugs => {
    const wrap = d.createElement('div');
    wrap.className = 'kc-cards';
    slugs.map(s => P[s]).filter(Boolean).forEach(p => {
      const a = d.createElement('a');
      a.className = 'kc-card';
      a.href = p.url;
      a.innerHTML = `<div class="kc-card__img${p.contain ? ' is-contain' : ''}"><img src="${p.thumb}" alt="${esc(p.name)}" loading="lazy"></div>
        <div class="kc-card__b"><b>${esc(p.name)}</b><span>${esc([p.location, p.area].filter(Boolean).join(' · '))}</span></div>`;
      wrap.append(a);
    });
    body.append(wrap);
  };

  const renderCta = ({ label, href, gold }) => {
    const a = d.createElement('a');
    a.className = 'kc-cta' + (gold ? ' kc-cta--gold' : '');
    a.href = href;
    if (/^https?:/.test(href)) { a.target = '_blank'; a.rel = 'noopener'; }
    a.innerHTML = (gold ? '' : icon.wa) + `<span>${esc(label)}</span>`;
    body.append(a);
  };

  const renderChips = chips => {
    const wrap = d.createElement('div');
    wrap.className = 'kc-chips';
    chips.forEach(([label, action]) => {
      const b = d.createElement('button');
      b.type = 'button';
      b.className = 'kc-chip';
      b.textContent = label;
      b.addEventListener('click', () => {
        wrap.classList.add('is-used');
        userSay(label, action);
      });
      wrap.append(b);
    });
    body.append(wrap);
  };

  const userSay = (text, action) => {
    body.querySelectorAll('.kc-chips:not(.is-used)').forEach(c => c.classList.add('is-used'));
    const m = d.createElement('div');
    m.className = 'kc-msg kc-msg--user';
    m.textContent = text;
    body.append(m);
    scroll();
    enqueue(() => sleep(250));
    handle(text, action);
  };

  /* ---------- Cérebro ---------- */
  const MAIN_CHIPS = [
    ['Ver lançamentos', 'lancamentos'],
    ['Agendar visita', 'visita'],
    ['Valores e condições', 'preco'],
    ['Falar com corretor', 'humano']
  ];

  const PROJECT_KEYS = [
    ['mon-tresor', ['mon tresor', 'montresor', 'tresor', 'sagrada familia']],
    ['haus', ['haus', 'house']],
    ['azure', ['azure', 'tabatinga', 'caragua', 'caraguatatuba']],
    ['monte-cristo', ['monte cristo', 'cristo']],
    ['monte-negro', ['monte negro', 'montenegro', 'negro']],
    ['monte-zurich', ['zurich', 'zurique']],
    ['altos-do-parque', ['altos do parque', 'altos']],
    ['serra-do-sincora', ['sincora', 'siroca']]
  ];

  const INTENTS = [
    ['humano', ['corretor', 'atendente', 'humano', 'pessoa real', 'falar com alguem', 'vendedor']],
    ['visita', ['visita', 'visitar', 'agendar', 'agenda', 'conhecer pessoalmente', 'decorado', 'stand', 'marcar']],
    ['financiamento', ['financia', 'fgts', 'entrada', 'parcela', 'banco', 'credito', 'caixa', 'permuta']],
    ['preco', ['preco', 'valor', 'quanto custa', 'custa', 'tabela', 'orcamento', 'caro', 'barato', 'investimento', 'condic']],
    ['plantas', ['planta', 'metragem', 'm2', 'metros', 'quarto', 'dormitorio', 'suite', 'tamanho', 'vaga']],
    ['lazer', ['lazer', 'piscina', 'academia', 'churrasq', 'playground', 'sauna', 'coworking', 'area comum', 'salao']],
    ['lancamentos', ['lancamento', 'lancamentos', 'novo', 'novidade', 'na planta', 'em obra', 'obra']],
    ['portfolio', ['empreendimentos', 'portfolio', 'todos', 'entregue', 'pronto', 'opcoes', 'apartamentos', 'imoveis', 'apartamento', 'imovel', 'ape']],
    ['localizacao', ['onde', 'endereco', 'localiza', 'regiao', 'bairro', 'fica', 'mapa', 'escritorio', 'sjc', 'sao jose']],
    ['vila-ema', ['vila ema']],
    ['litoral', ['praia', 'litoral', 'mar ']],
    ['contato', ['contato', 'telefone', 'whats', 'zap', 'ligar', 'email', 'instagram', 'insta']],
    ['sobre', ['quem sao', 'quem e a kyma', 'empresa', 'kyma', 'historia', 'sobre voces', 'construtora', 'confiavel']],
    ['obrigado', ['obrigad', 'valeu', 'agradeco', 'show', 'top', 'perfeito', 'massa']],
    ['tchau', ['tchau', 'ate mais', 'ate logo', 'falou']],
    ['oi', ['oi', 'ola', 'bom dia', 'boa tarde', 'boa noite', 'e ai', 'eai', 'hello', 'hey']]
  ];

  const has = (t, k) => (` ${t} `).includes(` ${k}`) || (k.includes(' ') && t.includes(k));
  const detect = t => {
    let intent = null;
    for (const [name, keys] of INTENTS) if (keys.some(k => has(t, k))) { intent = name; break; }
    for (const [slug, keys] of PROJECT_KEYS) if (keys.some(k => has(t, k))) return { type: 'project', slug, also: intent };
    return intent ? { type: intent } : null;
  };
  // perguntas que combinam com um empreendimento ("valor do haus", "visitar o azure")
  const COMBO = ['visita', 'preco', 'financiamento', 'humano'];

  const NOT_NAMES = ['sim', 'nao', 'ok', 'talvez', 'quero', 'pode', 'claro', 'blz', 'beleza', 'certo', 'isso'];
  const extractName = raw => {
    let s = raw.trim().replace(/[!.?,;]+$/g, '');
    s = s.replace(/^(meu nome (e|é)|me chamo|eu sou (o|a)?|sou (o|a)?|aqui (e|é) (o|a)?|pode me chamar de)\s+/i, '');
    const words = s.split(/\s+/).filter(Boolean);
    if (!words.length || words.length > 4 || s.length > 40) return null;
    if (!/^[\p{L}' -]+$/u.test(s)) return null;
    if (NOT_NAMES.includes(norm(words[0]))) return null;
    const first = words[0];
    return first.charAt(0).toUpperCase() + first.slice(1).toLowerCase();
  };
  const hi = () => (state.name ? `, ${state.name}` : '');

  const projectLine = p => {
    const bits = [p.location, p.area, p.beds].filter(Boolean).join(' · ');
    return `**${p.name}** — ${p.pitch}\n${bits}`;
  };

  const periodOf = t => {
    const wk = /sabado|domingo|fim de semana|final de semana|fds/.test(t);
    if (wk && /manha|cedo/.test(t)) return 'fim de semana, pela manhã';
    if (wk && /tarde/.test(t)) return 'fim de semana, à tarde';
    if (/manha|cedo/.test(t)) return 'manhã';
    if (/tarde/.test(t)) return 'tarde';
    if (/noite/.test(t)) return 'noite';
    if (/sabado|domingo|fim de semana|final de semana|fds/.test(t)) return 'fim de semana';
    if (/qualquer|tanto faz|indiferente|flex/.test(t)) return 'horário flexível';
    return null;
  };

  const askPeriod = () => {
    state.awaiting = 'period';
    say(`Perfeito${hi()}! Qual período fica melhor pra você visitar${state.interest ? ` o **${state.interest}**` : ''}?`, {
      chips: [['Manhã', 'p:manhã'], ['Tarde', 'p:tarde'], ['Fim de semana', 'p:fim de semana'], ['Tanto faz', 'p:horário flexível']]
    });
  };

  const finishVisit = () => {
    state.awaiting = null;
    const msg = `Olá! ${state.name ? `Meu nome é ${state.name}. ` : ''}Vim pelo site e gostaria de agendar uma visita${state.interest ? ` ao ${state.interest}` : ''}. Período de preferência: ${state.period}.`;
    say(`Fechado! Deixei tudo anotado:\n• Empreendimento: **${state.interest || 'a definir com o corretor'}**\n• Período: **${state.period}**\n\nToca no botão abaixo que eu já te conecto com um corretor no WhatsApp, com a mensagem pronta. ✨`, {
      cta: { label: 'Confirmar pelo WhatsApp', href: wa(msg) },
      chips: [['Ver outros empreendimentos', 'portfolio'], ['Tenho outra dúvida', 'menu']]
    });
  };

  const respond = (intent, t) => {
    const type = intent && intent.type;

    if (type === 'project') {
      const p = P[intent.slug];
      state.interest = p.name;
      const chips = [['Agendar visita', 'visita'], ['Valores', 'preco']];
      if (p.slug === 'haus') chips.splice(1, 0, ['Plantas', 'plantas'], ['Lazer', 'lazer']);
      say(projectLine(p), { cards: [p.slug], chips: chips.concat([['Outros empreendimentos', 'portfolio']]) });
      return;
    }

    switch (type) {
      case 'oi':
        say(pick([`Olá${hi()}! Que bom te ver por aqui. Como posso te ajudar hoje?`, `Oi${hi()}! Tô por aqui pra te ajudar a encontrar o seu próximo endereço. Por onde começamos?`]), { chips: MAIN_CHIPS });
        break;
      case 'lancamentos':
        say(`Temos **${launches.length} lançamentos** acontecendo agora${hi()}. Cada um com uma proposta bem própria:`, {
          cards: launches.map(p => p.slug),
          chips: launches.map(p => [p.name, 'proj:' + p.slug]).concat([['Agendar visita', 'visita']])
        });
        break;
      case 'portfolio':
        say(`Aqui está o nosso portfólio completo — são **${K.projects.length} empreendimentos** entre o Vale do Paraíba e o Litoral Norte. Arrasta pro lado pra ver todos 👉`, {
          cards: K.projects.map(p => p.slug),
          chips: [['Só lançamentos', 'lancamentos'], ['Agendar visita', 'visita'], ['Ver página completa', 'goto:/empreendimentos']]
        });
        break;
      case 'vila-ema':
        say('Na Vila Ema, uma das regiões mais desejadas de São José dos Campos, temos dois lançamentos: o **Haus** (2 dormitórios, 79,95m² e 82,21m²) e o **Mon Trésor** (114,66m², em frente à Igreja Sagrada Família).', {
          cards: ['haus', 'mon-tresor'], chips: [['Haus', 'proj:haus'], ['Mon Trésor', 'proj:mon-tresor'], ['Agendar visita', 'visita']]
        });
        break;
      case 'litoral':
        respond({ type: 'project', slug: 'azure' }, t);
        break;
      case 'visita':
        if (!state.interest) {
          state.awaiting = 'visit-project';
          say(`Ótima escolha${hi()} — nada como sentir o lugar de perto. Qual empreendimento você quer conhecer?`, {
            chips: launches.map(p => [p.name, 'vp:' + p.slug]).concat([['Ainda não sei', 'vp:none']])
          });
        } else askPeriod();
        break;
      case 'preco':
        say(`Os valores variam conforme a unidade, o andar e a condição de pagamento${hi()} — por isso a gente prefere te passar a **tabela atualizada** direto com um corretor, sem surpresa nenhuma.${state.interest ? `\n\nQuer que eu peça a tabela do **${state.interest}**?` : '\n\nDe qual empreendimento você quer a tabela?'}`, state.interest ? {
          cta: { label: `Receber tabela do ${state.interest}`, href: wa(`Olá! ${state.name ? `Sou ${state.name}. ` : ''}Gostaria de receber a tabela de valores do ${state.interest}.`) },
          chips: [['Financiamento', 'financiamento'], ['Agendar visita', 'visita']]
        } : { chips: launches.map(p => [p.name, 'price:' + p.slug]).concat([['Financiamento', 'financiamento']]) });
        break;
      case 'financiamento':
        say('Trabalhamos com condições facilitadas e nosso time te orienta em cada etapa: simulação, entrada, uso de FGTS e financiamento bancário. O ideal é fazer uma **simulação personalizada** com um corretor — é rápido e sem compromisso.', {
          cta: { label: 'Fazer simulação', href: wa(`Olá! ${state.name ? `Sou ${state.name}. ` : ''}Gostaria de simular condições de pagamento${state.interest ? ` para o ${state.interest}` : ''}.`) },
          chips: [['Ver lançamentos', 'lancamentos'], ['Agendar visita', 'visita']]
        });
        break;
      case 'plantas':
        say('No **Haus** são plantas de **79,95m² e 82,21m²**, com 2 dormitórios (1 suíte), área gourmet com churrasqueira e 2 vagas cobertas no subsolo.\nNo **Mon Trésor**, a planta tem **114,66m²**.\nJá no portfólio: Monte Cristo (65,76m²), Monte Negro (68,94m²) e Monte Zurich (69,60m²).', {
          chips: [['Ver plantas do Haus', 'goto:/haus#plantas'], ['Agendar visita', 'visita'], ['Valores', 'preco']]
        });
        break;
      case 'lazer':
        say('O **Haus** tem um lazer completo: piscina adulto e infantil com deck molhado e borda infinita, academia, sauna, solarium, coworking indoor e outdoor, salão de festas, sala de jogos, brinquedoteca, playground, espaço lareira e até carregamento veicular. ⚡', {
          cards: ['haus'], chips: [['Agendar visita', 'visita'], ['Plantas', 'plantas'], ['Valores', 'preco']]
        });
        break;
      case 'localizacao':
        say(`Nosso escritório fica na **${K.address}**.\n\nOs empreendimentos estão em São José dos Campos (Vila Ema e região) e no Litoral Norte (Tabatinga, Caraguatatuba).`, {
          cta: { label: 'Abrir no mapa', href: K.mapsUrl, gold: true },
          chips: [['Vila Ema', 'vila-ema'], ['Litoral Norte', 'proj:azure'], ['Contato', 'contato']]
        });
        break;
      case 'contato':
        say(`Você fala com a gente por aqui:\n📞 **${K.phone}**\n📍 ${K.address}\n📷 @${K.instagram}\n\nOu, se preferir, te conecto agora mesmo no WhatsApp.`, {
          cta: { label: 'Chamar no WhatsApp', href: wa('Olá! Vim pelo site da Kyma e gostaria de mais informações.') },
          chips: [['Ver lançamentos', 'lancamentos'], ['Agendar visita', 'visita']]
        });
        break;
      case 'sobre':
        say('A **Kyma Empreendimentos** atua na construção civil no Vale do Paraíba e no Litoral Norte de São Paulo. Nosso foco: empreendimentos atuais, com qualidade, boa localização e o retorno que o cliente espera.\n\nNossos valores: ética, transparência, credibilidade, compromisso, disciplina e criatividade.', {
          chips: [['Ver empreendimentos', 'portfolio'], ['Conhecer a Kyma', 'goto:/quem-somos']]
        });
        break;
      case 'humano':
        say(`Claro${hi()}! Um corretor de verdade vai te atender pelo WhatsApp. Já deixei a mensagem pronta${state.interest ? ` falando do **${state.interest}**` : ''}. 😉`, {
          cta: { label: 'Falar com corretor', href: wa(`Olá! ${state.name ? `Meu nome é ${state.name}. ` : ''}Vim pelo site da Kyma${state.interest ? ` e tenho interesse no ${state.interest}` : ''}. Pode me ajudar?`) }
        });
        break;
      case 'obrigado':
        say(pick([`Imagina${hi()}! Foi um prazer. Se surgir qualquer dúvida, é só chamar.`, `Eu que agradeço${hi()}! Tô sempre por aqui. ✨`]), { chips: [['Ver lançamentos', 'lancamentos'], ['Falar com corretor', 'humano']] });
        break;
      case 'morar':
        say(`Que demais${hi()}! Pra morar, o **Haus** costuma encantar: 2 dormitórios, conceito aberto, lazer de clube e uma das regiões mais completas de São José dos Campos. E pra quem busca mais espaço, o **Mon Trésor** tem 114,66m².`, {
          cards: ['haus', 'mon-tresor'], chips: [['Agendar visita', 'visita'], ['Lazer do Haus', 'lazer'], ['Valores', 'preco']]
        });
        break;
      case 'investir':
        say(`Ótima visão${hi()}! Nossos destaques no momento são o **Haus** e o **Mon Trésor**, na Vila Ema, e o **Azure**, no Litoral Norte. Um corretor pode te mostrar as condições de cada um.`, {
          cards: launches.map(p => p.slug), chips: [['Simular condições', 'financiamento'], ['Falar com corretor', 'humano']]
        });
        break;
      case 'tchau':
        say(`Até mais${hi()}! Quando quiser voltar, é só clicar no botão dourado aqui embaixo. 👋`);
        break;
      case 'menu':
        say('Claro! Sobre o que mais você quer saber?', { chips: MAIN_CHIPS.concat([['Localização', 'localizacao'], ['Sobre a Kyma', 'sobre']]) });
        break;
      default:
        say(pick([
          `Hmm, essa eu prefiro não chutar${hi()} — quero te passar só informação certa. Posso te ajudar com uma dessas opções ou te conectar com um corretor:`,
          `Boa pergunta! Pra não te responder nada errado, deixa eu te mostrar o que eu sei fazer por aqui:`
        ]), { chips: MAIN_CHIPS.concat([['Localização', 'localizacao']]) });
    }
  };

  const handle = (text, action) => {
    const t = norm(text);

    if (action) {
      if (action.startsWith('goto:')) {
        say('Te levando pra lá agora… 🚀');
        enqueue(() => sleep(500)).then(() => { location.href = action.slice(5); });
        return;
      }
      if (action.startsWith('proj:')) return respond({ type: 'project', slug: action.slice(5) }, t);
      if (action.startsWith('price:')) { state.interest = P[action.slice(6)].name; return respond({ type: 'preco' }, t); }
      if (action.startsWith('p:')) { state.period = action.slice(2); return finishVisit(); }
      if (action.startsWith('vp:')) {
        const slug = action.slice(3);
        state.interest = slug === 'none' ? null : P[slug].name;
        return askPeriod();
      }
      return respond({ type: action }, t);
    }

    const intent = detect(t);

    if (state.awaiting === 'name') {
      const name = !intent || intent.type === 'oi' ? extractName(text.replace(/^(oi|olá|ola|e aí|eai)[,!\s]*/i, '')) : null;
      if (name) {
        state.name = name;
        state.awaiting = null;
        store.set('kc-name', name);
        say(`Prazer, ${name}! 😊 Me conta: você está procurando um imóvel pra morar ou pra investir?`, {
          chips: [['Pra morar', 'morar'], ['Pra investir', 'investir'], ['Ver lançamentos', 'lancamentos']]
        });
        return;
      }
      state.awaiting = null;
    }

    if (state.awaiting === 'period') {
      const p = periodOf(t);
      if (p) { state.period = p; return finishVisit(); }
      state.awaiting = null;
    }

    if (state.awaiting === 'visit-project') {
      if (intent && intent.type === 'project') { state.interest = P[intent.slug].name; return askPeriod(); }
      state.awaiting = null;
    }

    const generic = !intent || intent.type === 'portfolio' || intent.type === 'oi';
    if (generic && /\bmorar\b|morad|familia|filhos/.test(t)) return respond({ type: 'morar' }, t);
    if (generic && /investi|renda|aluguel|rentab|valoriz/.test(t)) return respond({ type: 'investir' }, t);

    if (intent && intent.type === 'project' && COMBO.includes(intent.also)) {
      state.interest = P[intent.slug].name;
      return respond({ type: intent.also }, t);
    }
    respond(intent, t);
  };

  /* ---------- Abertura e saudação ---------- */
  const greet = () => {
    if (state.started) return;
    state.started = true;
    const saved = store.get('kc-name');
    if (saved) { state.name = saved; state.awaiting = null; }
    if (pageProject) {
      state.interest = pageProject.name;
      say(`Olá${hi()}! 👋 Sou a assistente virtual da Kyma.`);
      say(`Vi que você está conhecendo o **${pageProject.name}**. Quer que eu te conte os destaques, ou prefere já agendar uma visita?`, {
        chips: [['Destaques', 'proj:' + pageProject.slug], ['Agendar visita', 'visita'], ['Valores', 'preco'], ['Outros empreendimentos', 'portfolio']]
      });
      if (!state.name) state.awaiting = null;
      return;
    }
    if (state.name) {
      say(`Que bom te ver de novo, ${state.name}! ✨ Em que posso te ajudar agora?`, { chips: MAIN_CHIPS });
      return;
    }
    say('Olá! 👋 Sou a assistente virtual da **Kyma Empreendimentos**.');
    say('Posso te apresentar nossos lançamentos, tirar dúvidas sobre plantas e localização ou agendar uma visita com um corretor. Antes, como posso te chamar?', {
      chips: [['Ver lançamentos', 'lancamentos'], ['Agendar visita', 'visita'], ['Falar com corretor', 'humano']]
    });
  };

  const open = () => {
    root.classList.add('kc-open', 'kc-seen');
    launch.setAttribute('aria-expanded', 'true');
    launch.setAttribute('aria-label', 'Fechar chat');
    teaser.classList.remove('is-show');
    store.set('kc-seen', '1');
    greet();
    setTimeout(() => { if (matchMedia('(pointer: fine)').matches) input.focus(); }, 400);
  };
  const close = () => {
    root.classList.remove('kc-open');
    launch.setAttribute('aria-expanded', 'false');
    launch.setAttribute('aria-label', 'Abrir chat com a assistente virtual');
  };

  launch.addEventListener('click', () => (root.classList.contains('kc-open') ? close() : open()));
  teaser.addEventListener('click', e => {
    if (e.target.closest('.kc-teaser__x')) { teaser.classList.remove('is-show'); store.set('kc-seen', '1'); return; }
    open();
  });
  d.addEventListener('keydown', e => { if (e.key === 'Escape' && root.classList.contains('kc-open')) close(); });

  input.addEventListener('input', () => { sendBtn.disabled = !input.value.trim(); });
  form.addEventListener('submit', e => {
    e.preventDefault();
    const v = input.value.trim();
    if (!v) return;
    input.value = '';
    sendBtn.disabled = true;
    userSay(v);
  });

  // Teaser com efeito de digitação depois de alguns segundos
  if (store.get('kc-seen')) root.classList.add('kc-seen');
  else {
    setTimeout(() => {
      if (root.classList.contains('kc-open')) return;
      const span = teaser.querySelector('.kc-teaser__t');
      const txt = pageProject ? `Quer saber mais sobre o ${pageProject.name}? Posso te ajudar! ✨` : 'Oi! 👋 Posso te ajudar a encontrar o apê ideal?';
      teaser.classList.add('is-show');
      let i = 0;
      const tick = () => { span.textContent = txt.slice(0, ++i); if (i < txt.length) setTimeout(tick, 28); };
      reduce ? (span.textContent = txt) : tick();
    }, 6500);
  }
})();
