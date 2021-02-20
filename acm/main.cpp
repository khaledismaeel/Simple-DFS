#include <bits/stdc++.h>

using namespace std;

typedef long long ll;

struct DSU {
  vector<int> par;
  DSU(int n) {
    par.resize(n);
    for (int i = 0; i < n; i++)
      par[i] = i;
  }
  int comp(int x) {
    if (x == par[x])
      return x;
    return par[x] = comp(par[x]);
  }
  void mrg(int x, int y) {
    par[comp(y)] = comp(x);
  }
};

int conn_comp(int n, const vector<pair<int, int>> &graph) {
  int ret = n;
  DSU dsu(n);
  for (auto e : graph) {
    if (dsu.comp(e.first) != dsu.comp(e.second)) {
      dsu.mrg(e.first, e.second);
      ret--;
    }
  }
  return ret;
}

int main() {
  const ll MOD = 1000000007ll;
  int TC;
  cin >> TC;
  while (TC--) {
    ll n;
    cin >> n;
    vector<pair<int, int>> rooks;
    {
      for (int i = 0; i < 3; i++) {
        string s;
        cin >> s;
        for (int j = 0; j < 3; j++) {
          if (s[j] == 'x')
            rooks.push_back({i, j});
        }
      }
      sort(rooks.begin(), rooks.end());
    }
    vector<pair<int, int>> attack;
    {
      auto chk = [](pair<int, int> a, pair<int, int> b) {
        return a.first == b.first || a.second == b.second;
      };
      for (int i = 0; i < rooks.size(); i++) {
        for (int j = i + 1; j < rooks.size(); j++) {
          if (chk(rooks[i], rooks[j]))
            attack.push_back({i, j});
        }
      }
    }
    ll ans = 0;
    auto f = [MOD](ll n, ll k) {
      ll ret = 1;
      for (ll i = 0; i < k; i++)
        ret = (ret * n) % MOD;
      return ret;
    };
    for (int i = 0; i < (1 << attack.size()); i++) {
      ll sign = __builtin_popcount(i) % 2 == 0 ? 1ll : -1ll;
      vector<pair<int, int>> graph;
      for (int j = 0; j < attack.size(); j++) {
        if (i & (1 << j))
          graph.push_back(attack[j]);
      }
      ll k = conn_comp(rooks.size(), graph);
      ans = (ans + sign * f(n, k) + MOD) % MOD;
      
    }
    cout << ans << endl;
  }
  return 0;
}