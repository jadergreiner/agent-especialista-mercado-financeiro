# Pesquisa de Providers OAuth2 para Autenticação Forte

## Providers Avaliados

1. **Keycloak**
   - Open-source, flexível
   - Suporte RBAC avançado
   - Integração com FastAPI via python-keycloak
   - Custos: Hospedagem própria

2. **Auth0**
   - SaaS, fácil setup
   - Suporte multi-tenant
   - Custos: Baseado em usuários ativos
   - Integração via authlib

3. **Azure AD**
   - Se já usando Azure, integração nativa
   - Suporte enterprise
   - Custos: Parte do Azure subscription

## Recomendação Inicial

Keycloak para PoC, devido a custo zero e controle total.

Origin: TASK-27 - Autenticação forte PoC