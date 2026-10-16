/* =========================================================
   CRM — Worker de Cloudflare
   Sirve la web estática y recibe el formulario de presupuesto
   (POST /api/presupuesto), que envía por email a CRM.

   El envío usa Cloudflare Email Routing (binding "CORREO" en
   wrangler.jsonc). Mientras no esté configurado, el formulario
   responde con un aviso para llamar o escribir por WhatsApp.
   ========================================================= */

import { EmailMessage } from "cloudflare:email";

const REMITENTE = "web@crmgestiontaller.com"; // dominio con Email Routing activado
const DESTINO = "info@crmsl.es"; // debe estar verificado en Email Routing
const MAX_FOTOS = 4;
const MAX_BYTES_FOTO = 6 * 1024 * 1024;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/presupuesto") {
      if (request.method !== "POST") return new Response("Método no permitido", { status: 405 });
      return presupuesto(request, env);
    }
    return env.ASSETS.fetch(request);
  },
};

async function presupuesto(request, env) {
  const quiereJson = (request.headers.get("Accept") || "").includes("application/json");
  const responder = (ok, mensaje, estado = 200) =>
    quiereJson
      ? Response.json({ ok, mensaje }, { status: estado })
      : Response.redirect(new URL(ok ? "/presupuesto/gracias/" : "/presupuesto/?error=1", request.url), 303);

  let datos;
  try {
    datos = await request.formData();
  } catch {
    return responder(false, "No se han podido leer los datos del formulario.", 400);
  }
  const campo = (n) => String(datos.get(n) || "").trim().slice(0, 4000);

  // Antispam: campo trampa invisible y tiempo mínimo para rellenarlo
  const inicio = Number(campo("t")) || 0;
  if (campo("web") || (inicio && Date.now() - inicio < 3000)) {
    return responder(true, "Gracias."); // al robot se le responde como si hubiera ido bien
  }

  const nombre = campo("nombre");
  const telefono = campo("telefono");
  const email = campo("email");
  if (!nombre || (!telefono && !email)) {
    return responder(false, "Indica tu nombre y un teléfono o email para poder contestarte.", 400);
  }
  if (!campo("privacidad")) {
    return responder(false, "Debes aceptar la política de privacidad.", 400);
  }

  if (!env.CORREO) {
    return responder(false, "El formulario todavía no está activo. Llámanos al 957 682 819 o escríbenos por WhatsApp al 656 84 40 67.", 503);
  }

  const fotos = datos
    .getAll("fotos")
    .filter((f) => f && typeof f === "object" && f.size > 0 && f.size <= MAX_BYTES_FOTO && /^image\//.test(f.type))
    .slice(0, MAX_FOTOS);

  const texto = [
    "Nueva solicitud de presupuesto desde la web",
    "",
    `Nombre:    ${nombre}`,
    `Empresa:   ${campo("empresa") || "-"}`,
    `Teléfono:  ${telefono || "-"}`,
    `Email:     ${email || "-"}`,
    `Producto:  ${campo("producto") || "-"}`,
    `Cantidad:  ${campo("cantidad") || "-"}`,
    "",
    "Medidas / descripción:",
    campo("mensaje") || "-",
    "",
    fotos.length ? `Fotos adjuntas: ${fotos.length}` : "Sin fotos adjuntas.",
  ].join("\r\n");

  const raw = await construirEmail({
    asunto: `Presupuesto web: ${campo("producto") || "consulta"} — ${nombre}`,
    texto,
    responderA: email,
    fotos,
  });

  try {
    await env.CORREO.send(new EmailMessage(REMITENTE, DESTINO, raw));
  } catch (err) {
    console.error("Error al enviar el email", err);
    return responder(false, "No se ha podido enviar. Llámanos al 957 682 819 o escríbenos por WhatsApp al 656 84 40 67.", 502);
  }
  return responder(true, "¡Gracias! Hemos recibido tu solicitud y te contestaremos lo antes posible.");
}

/* Construye un email MIME (texto + fotos adjuntas) sin librerías externas. */
async function construirEmail({ asunto, texto, responderA, fotos }) {
  const limite = "crm-" + crypto.randomUUID();
  const cabeceras = [
    `From: Web CRM <${REMITENTE}>`,
    `To: ${DESTINO}`,
    `Subject: ${codificarCabecera(asunto)}`,
    `Date: ${new Date().toUTCString()}`,
    `Message-ID: <${crypto.randomUUID()}@crmgestiontaller.com>`,
    "MIME-Version: 1.0",
    `Content-Type: multipart/mixed; boundary="${limite}"`,
  ];
  if (responderA && /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(responderA)) cabeceras.push(`Reply-To: ${responderA}`);

  const partes = [
    [
      `--${limite}`,
      "Content-Type: text/plain; charset=UTF-8",
      "Content-Transfer-Encoding: base64",
      "",
      base64Lineas(new TextEncoder().encode(texto)),
    ].join("\r\n"),
  ];
  for (const [i, foto] of fotos.entries()) {
    const ext = (foto.type.split("/")[1] || "jpg").replace("jpeg", "jpg");
    partes.push(
      [
        `--${limite}`,
        `Content-Type: ${foto.type}; name="foto-${i + 1}.${ext}"`,
        `Content-Disposition: attachment; filename="foto-${i + 1}.${ext}"`,
        "Content-Transfer-Encoding: base64",
        "",
        base64Lineas(new Uint8Array(await foto.arrayBuffer())),
      ].join("\r\n")
    );
  }
  return cabeceras.join("\r\n") + "\r\n\r\n" + partes.join("\r\n") + `\r\n--${limite}--\r\n`;
}

function codificarCabecera(texto) {
  return "=?UTF-8?B?" + base64(new TextEncoder().encode(texto)) + "?=";
}

function base64(bytes) {
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

function base64Lineas(bytes) {
  return base64(bytes).replace(/.{76}/g, "$&\r\n");
}
